"""
Module 9: Content Planner – Social Media Post Calendar
"""
import uuid
from typing import Optional, List, TYPE_CHECKING
from datetime import date, datetime
from sqlalchemy import String, Text, Boolean, ForeignKey, Date, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from app.models.mixins import UUID, UUIDMixin, TimestampMixin
import enum

if TYPE_CHECKING:
    from app.models.club import Club


class PostPlatform(str, enum.Enum):
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    WHATSAPP = "whatsapp"
    OTHER = "other"


class PostStatus(str, enum.Enum):
    DRAFT = "draft"
    READY = "ready"
    PUBLISHED = "published"
    CANCELLED = "cancelled"


class ContentPlan(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "content_plans"

    club_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    club: Mapped["Club"] = relationship(back_populates="content_plans")
    post_entries: Mapped[List["PostEntry"]] = relationship(back_populates="plan", cascade="all, delete-orphan")


class PostEntry(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "post_entries"

    plan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("content_plans.id", ondelete="CASCADE"), nullable=False)
    assigned_to_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    caption: Mapped[Optional[str]] = mapped_column(Text)
    platform: Mapped[PostPlatform] = mapped_column(SAEnum(PostPlatform), default=PostPlatform.INSTAGRAM)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[PostStatus] = mapped_column(SAEnum(PostStatus), default=PostStatus.DRAFT)
    media_url: Mapped[Optional[str]] = mapped_column(String(500))

    plan: Mapped["ContentPlan"] = relationship(back_populates="post_entries")
