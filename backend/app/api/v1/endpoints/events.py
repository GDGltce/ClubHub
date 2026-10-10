"""
Event endpoints with lifecycle stage management
"""
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, date, time, timedelta, timezone
import uuid
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.event import Event, EventStage, EventStatus
from app.schemas.event import EventCreate, EventUpdate, EventOut, EventStageAdvance
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/events", tags=["Events"])

STAGE_ORDER = [s for s in EventStatus]


@router.get("", response_model=List[EventOut])
def list_events(
    club_id: Optional[str] = None,
    stage: Optional[EventStatus] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Event).filter(Event.visibility == "public")
    if club_id:
        try:
            uuid.UUID(club_id)
        except ValueError:
            return []
        q = q.filter(Event.club_id == club_id)
    if stage:
        q = q.filter(Event.stage == stage)
    if date_from or date_to:
        q = q.filter(Event.start_datetime.isnot(None))
        if date_from:
            q = q.filter(Event.start_datetime >= datetime.combine(date_from, time.min, tzinfo=timezone.utc))
        if date_to:
            q = q.filter(Event.start_datetime < datetime.combine(date_to + timedelta(days=1), time.min, tzinfo=timezone.utc))
    return q.order_by(Event.start_datetime.is_(None), Event.start_datetime.asc()).all()


@router.post("", response_model=EventOut, status_code=201)
def create_event(body: EventCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    event = Event(**body.model_dump(), created_by_id=current_user.id, stage=EventStatus.IDEA)
    db.add(event)
    db.flush()
    stage_log = EventStage(event_id=event.id, stage=EventStatus.IDEA, moved_by_id=current_user.id)
    db.add(stage_log)
    db.commit()
    db.refresh(event)
    return event


@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: str, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(404, "Event not found")
    return event


@router.patch("/{event_id}", response_model=EventOut)
def update_event(event_id: str, body: EventUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(404, "Event not found")
    if event.is_locked:
        raise HTTPException(400, "Event is archived and locked")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(event, k, v)
    db.commit()
    db.refresh(event)
    return event


@router.post("/{event_id}/advance-stage", response_model=EventOut)
def advance_stage(
    event_id: str, body: EventStageAdvance,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(404, "Event not found")
    if event.is_locked:
        raise HTTPException(400, "Event is archived")
    current_idx = STAGE_ORDER.index(event.stage)
    if current_idx >= len(STAGE_ORDER) - 1:
        raise HTTPException(400, "Already at final stage")
    next_stage = STAGE_ORDER[current_idx + 1]
    event.stage = next_stage
    if next_stage == EventStatus.ARCHIVED:
        event.is_locked = True
    stage_log = EventStage(event_id=event.id, stage=next_stage, moved_by_id=current_user.id, notes=body.notes)
    db.add(stage_log)
    db.commit()
    db.refresh(event)
    return event
