"""
Module 4: Events and Event Lifecycle
"""
import uuid
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, Text, Integer, Boolean, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from app.models.mixins import UUID, UUIDMixin, TimestampMixin
import enum

if TYPE_CHECKING:
    from app.models.club import Club
    from app.models.document import Document
    from app.models.media import Photo
    from app.models.finance import Expense


class EventStatus(str, enum.Enum):
    IDEA = "idea"
    PERMISSION = "permission"
    FUNDS = "funds"
    PLANNING = "planning"
    PROMOTION = "promotion"
    PRE_EVENT = "pre_event"
    EXECUTION = "execution"
    POST_EVENT = "post_event"
    ARCHIVED = "archived"


class EventVisibility(str, enum.Enum):
    PUBLIC = "public"
    MEMBERS_ONLY = "members_only"
    CLUB_LEADS_ONLY = "club_leads_only"


class Event(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "events"

    club_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    created_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    goal: Mapped[Optional[str]] = mapped_column(Text)
    expected_turnout: Mapped[Optional[int]] = mapped_column(Integer)
    audience: Mapped[Optional[str]] = mapped_column(String(255))
    venue: Mapped[Optional[str]] = mapped_column(String(255))
    start_datetime: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    end_datetime: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    stage: Mapped[EventStatus] = mapped_column(SAEnum(EventStatus), default=EventStatus.IDEA)
    visibility: Mapped[EventVisibility] = mapped_column(SAEnum(EventVisibility), default=EventVisibility.PUBLIC)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)
    registration_link: Mapped[Optional[str]] = mapped_column(String(500))
    feedback_summary: Mapped[Optional[str]] = mapped_column(Text)
    lessons_learned: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    club: Mapped["Club"] = relationship(back_populates="events")
    stage_history: Mapped[List["EventStage"]] = relationship(back_populates="event", cascade="all, delete-orphan")
    documents: Mapped[List["Document"]] = relationship(back_populates="event")


class EventStage(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "event_stages"

    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    stage: Mapped[EventStatus] = mapped_column(SAEnum(EventStatus), nullable=False)
    moved_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    event: Mapped["Event"] = relationship(back_populates="stage_history")
