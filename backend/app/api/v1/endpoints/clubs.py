"""
Club endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.club import Club, ClubStatus
from app.schemas.club import ClubCreate, ClubUpdate, ClubOut
from app.api.deps import get_current_user, require_admin
from app.models.user import User

router = APIRouter(prefix="/clubs", tags=["Clubs"])


@router.get("", response_model=List[ClubOut])
def list_clubs(
    college_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    q = db.query(Club).filter(Club.is_public == True, Club.status == ClubStatus.ACTIVE)
    if college_id:
        q = q.filter(Club.college_id == college_id)
    return q.all()


@router.post("", response_model=ClubOut, status_code=201)
def create_club(body: ClubCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    club = Club(**body.model_dump(), status=ClubStatus.PENDING)
    db.add(club)
    db.commit()
    db.refresh(club)
    return club


@router.get("/pending", response_model=List[ClubOut])
def list_pending_clubs(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return (
        db.query(Club)
        .filter(Club.status == ClubStatus.PENDING)
        .order_by(Club.created_at.asc())
        .all()
    )


@router.get("/{club_id}", response_model=ClubOut)
def get_club(club_id: str, db: Session = Depends(get_db)):
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(404, "Club not found")
    return club


@router.patch("/{club_id}", response_model=ClubOut)
def update_club(club_id: str, body: ClubUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(404, "Club not found")
    changes = body.model_dump(exclude_unset=True)
    for k, v in changes.items():
        setattr(club, k, v)
    if changes and club.status == ClubStatus.NEEDS_CHANGES:
        club.status = ClubStatus.PENDING
    db.commit()
    db.refresh(club)
    return club


@router.patch("/{club_id}/approve", response_model=ClubOut)
def approve_club(club_id: str, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(404, "Club not found")
    if club.status != ClubStatus.PENDING:
        raise HTTPException(status.HTTP_409_CONFLICT, "Only pending clubs can be reviewed")
    club.status = ClubStatus.ACTIVE
    db.commit()
    db.refresh(club)
    return club


@router.patch("/{club_id}/send-back", response_model=ClubOut)
def send_back_club(club_id: str, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(404, "Club not found")
    if club.status != ClubStatus.PENDING:
        raise HTTPException(status.HTTP_409_CONFLICT, "Only pending clubs can be reviewed")
    club.status = ClubStatus.NEEDS_CHANGES
    db.commit()
    db.refresh(club)
    return club
