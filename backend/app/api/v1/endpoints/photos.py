"""Photo endpoints for clubs"""

import os
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.media import Album, Photo
from app.models.club import Club
from app.schemas.media import PhotoOut, AlbumOut
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/clubs", tags=["Club Photos"])  # We'll mount under /clubs/{club_id}/photos

def get_or_create_default_album(db: Session, club: Club) -> Album:
    album = (
        db.query(Album)
        .filter(Album.club_id == club.id, Album.title == "Club Photos")
        .first()
    )
    if not album:
        album = Album(club_id=club.id, title="Club Photos", description="Auto‑generated album for club photos")
        db.add(album)
        db.commit()
        db.refresh(album)
    return album

@router.post("/{club_id}/photos", response_model=PhotoOut, status_code=201)
async def upload_photo(
    club_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    # Optionally add permission checks here (e.g., only members can upload)

    album = get_or_create_default_album(db, club)

    # Ensure upload directory exists
    upload_root = Path("backend/app/static/uploads")
    club_dir = upload_root / f"club_{club_id}"
    os.makedirs(club_dir, exist_ok=True)

    # Save file with a unique name to avoid collisions
    ext = Path(file.filename).suffix
    filename = f"{uuid4().hex}{ext}"
    file_path = club_dir / filename
    async with file as f:
        contents = await f.read()
        with open(file_path, "wb") as out_file:
            out_file.write(contents)

    # Build URL that matches the static mount we added in main.py
    url = f"/uploads/club_{club_id}/{filename}"

    photo = Photo(album_id=album.id, uploaded_by_id=current_user.id, url=url)
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return PhotoOut.from_orm(photo)

@router.get("/{club_id}/photos", response_model=list[PhotoOut])
def list_photos(
    club_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    photos = (
        db.query(Photo)
        .join(Album, Photo.album_id == Album.id)
        .filter(Album.club_id == club.id)
        .all()
    )
    return [PhotoOut.from_orm(p) for p in photos]
