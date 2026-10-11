
"""Media Gallery API: albums, image uploads, and photo management."""

from io import BytesIO
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.club import Club
from app.models.event import Event
from app.models.media import Album, Photo, PhotoTag
from app.models.membership import ClubRole, Membership
from app.models.user import GlobalRole, User
from app.schemas.media import AlbumCreate, AlbumOut, AlbumUpdate, PhotoOut


router = APIRouter(prefix="/media", tags=["Media Gallery"])

# Files are stored in backend/uploads/media.
UPLOAD_ROOT = Path(__file__).resolve().parents[4] / "uploads"
MEDIA_DIR = UPLOAD_ROOT / "media"
THUMBNAIL_DIR = MEDIA_DIR / "thumbnails"

MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_IMAGE_PIXELS = 20_000_000
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}

OFFICER_ROLES = {
    ClubRole.PRESIDENT,
    ClubRole.SECRETARY,
    ClubRole.TREASURER,
}


def get_membership(db: Session, user_id: UUID, club_id: UUID):
    return (
        db.query(Membership)
        .filter(
            Membership.user_id == user_id,
            Membership.club_id == club_id,
            Membership.is_active.is_(True),
        )
        .first()
    )


def is_admin(user: User) -> bool:
    return user.global_role in {
        GlobalRole.PLATFORM_ADMIN,
        GlobalRole.FACULTY_COORDINATOR,
    }


def can_upload(db: Session, user: User, club_id: UUID) -> bool:
    return is_admin(user) or get_membership(db, user.id, club_id) is not None


def can_manage_album(db: Session, user: User, club_id: UUID) -> bool:
    if is_admin(user):
        return True

    membership = get_membership(db, user.id, club_id)
    return membership is not None and membership.role in OFFICER_ROLES


def remove_stored_file(url: str | None) -> None:
    """Delete only files belonging to this gallery's storage directory."""
    if not url:
        return

    filename = url.rsplit("/", 1)[-1]
    if not filename or filename in {".", ".."}:
        return

    for directory in (MEDIA_DIR, THUMBNAIL_DIR):
        path = directory / filename
        if path.is_file():
            path.unlink(missing_ok=True)


def save_image(data: bytes) -> tuple[str, str]:
    """Validate and re-encode an image, then create a thumbnail."""
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)

    try:
        with Image.open(BytesIO(data)) as source:
            if source.format not in ALLOWED_FORMATS:
                raise HTTPException(
                    status_code=415,
                    detail="Only JPEG, PNG, and WEBP images are supported.",
                )

            if source.width * source.height > MAX_IMAGE_PIXELS:
                raise HTTPException(
                    status_code=413,
                    detail="Image dimensions are too large.",
                )

            source.verify()

        with Image.open(BytesIO(data)) as source:
            image = ImageOps.exif_transpose(source)
            image.load()

            image_format = source.format
            extension = {
                "JPEG": ".jpg",
                "PNG": ".png",
                "WEBP": ".webp",
            }[image_format]

            filename = f"{uuid4().hex}{extension}"
            image_path = MEDIA_DIR / filename

            if image_format == "JPEG":
                image = image.convert("RGB")
                image.save(image_path, format="JPEG", quality=90, optimize=True)
            elif image_format == "PNG":
                image.save(image_path, format="PNG", optimize=True)
            else:
                image.save(image_path, format="WEBP", quality=90, method=4)

            thumbnail = image.convert("RGB")
            thumbnail.thumbnail((500, 500))
            thumbnail_name = f"{Path(filename).stem}.jpg"
            thumbnail.save(
                THUMBNAIL_DIR / thumbnail_name,
                format="JPEG",
                quality=85,
                optimize=True,
            )

            return (
                f"/uploads/media/{filename}",
                f"/uploads/media/thumbnails/{thumbnail_name}",
            )

    except HTTPException:
        raise
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid supported image.",
        ) from None


@router.post("/albums", response_model=AlbumOut, status_code=201)
def create_album(
    payload: AlbumCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    club = db.query(Club).filter(Club.id == payload.club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found.")

    if not can_manage_album(db, current_user, payload.club_id):
        raise HTTPException(
            status_code=403,
            detail="Only club officers or administrators can create albums.",
        )

    if payload.event_id:
        event = db.query(Event).filter(Event.id == payload.event_id).first()
        if not event or event.club_id != payload.club_id:
            raise HTTPException(
                status_code=400,
                detail="The event must belong to the selected club.",
            )

    album = Album(**payload.model_dump())
    db.add(album)
    db.commit()
    db.refresh(album)
    return album


@router.get("/albums", response_model=list[AlbumOut])
def list_albums(
    club_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Album)

    if club_id:
        query = query.filter(Album.club_id == club_id)

    albums = query.order_by(Album.created_at.desc()).all()

    if is_admin(current_user):
        return albums

    memberships = (
        db.query(Membership.club_id)
        .filter(
            Membership.user_id == current_user.id,
            Membership.is_active.is_(True),
        )
        .all()
    )
    member_club_ids = {row[0] for row in memberships}

    return [
        album
        for album in albums
        if album.is_public or album.club_id in member_club_ids
    ]


@router.patch("/albums/{album_id}", response_model=AlbumOut)
def update_album(
    album_id: UUID,
    payload: AlbumUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    album = db.query(Album).filter(Album.id == album_id).first()
    if not album:
        raise HTTPException(status_code=404, detail="Album not found.")

    if not can_manage_album(db, current_user, album.club_id):
        raise HTTPException(status_code=403, detail="Permission denied.")

    if payload.model_fields_set == set():
        return album

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(album, field, value)

    db.commit()
    db.refresh(album)
    return album


@router.delete("/albums/{album_id}", status_code=204)
def delete_album(
    album_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    album = db.query(Album).filter(Album.id == album_id).first()
    if not album:
        raise HTTPException(status_code=404, detail="Album not found.")

    if not can_manage_album(db, current_user, album.club_id):
        raise HTTPException(status_code=403, detail="Permission denied.")

    photos = list(album.photos)
    for photo in photos:
        remove_stored_file(photo.url)
        remove_stored_file(photo.thumbnail_url)

    db.delete(album)
    db.commit()


@router.post(
    "/albums/{album_id}/photos",
    response_model=PhotoOut,
    status_code=201,
)
async def upload_photo(
    album_id: UUID,
    file: UploadFile = File(...),
    caption: str | None = Form(default=None, max_length=500),
    tag: PhotoTag = Form(default=PhotoTag.GENERAL),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    album = db.query(Album).filter(Album.id == album_id).first()
    if not album:
        raise HTTPException(status_code=404, detail="Album not found.")

    if not can_upload(db, current_user, album.club_id):
        raise HTTPException(
            status_code=403,
            detail="Active club membership is required to upload photos.",
        )

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="Please upload an image.")

    data = await file.read(MAX_IMAGE_SIZE + 1)
    await file.close()

    if not data:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    if len(data) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image size must not exceed 10 MB.",
        )

    url, thumbnail_url = save_image(data)

    try:
        photo = Photo(
            album_id=album.id,
            uploaded_by_id=current_user.id,
            url=url,
            thumbnail_url=thumbnail_url,
            caption=caption,
            tag=tag,
        )
        db.add(photo)
        db.commit()
        db.refresh(photo)
        return photo
    except Exception:
        db.rollback()
        remove_stored_file(url)
        remove_stored_file(thumbnail_url)
        raise


@router.get("/albums/{album_id}/photos", response_model=list[PhotoOut])
def list_photos(
    album_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    album = db.query(Album).filter(Album.id == album_id).first()
    if not album:
        raise HTTPException(status_code=404, detail="Album not found.")

    membership = get_membership(db, current_user.id, album.club_id)
    if not album.is_public and not is_admin(current_user) and not membership:
        raise HTTPException(status_code=403, detail="Permission denied.")

    return (
        db.query(Photo)
        .filter(Photo.album_id == album_id)
        .order_by(Photo.created_at.desc())
        .all()
    )


@router.delete("/photos/{photo_id}", status_code=204)
def delete_photo(
    photo_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found.")

    album = db.query(Album).filter(Album.id == photo.album_id).first()
    if not album:
        raise HTTPException(status_code=404, detail="Album not found.")

    is_owner = photo.uploaded_by_id == current_user.id
    if not is_owner and not can_manage_album(db, current_user, album.club_id):
        raise HTTPException(status_code=403, detail="Permission denied.")

    remove_stored_file(photo.url)
    remove_stored_file(photo.thumbnail_url)

    db.delete(photo)
    db.commit()
