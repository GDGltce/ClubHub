"""
Module 7: Media Gallery – Albums and Photos
"""
import uuid
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Text, Boolean, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from app.models.mixins import UUID, UUIDMixin, TimestampMixin
import enum

if TYPE_CHECKING:
    from app.models.club import Club
    from app.models.event import Event


class PhotoTag(str, enum.Enum):
    BEFORE = "before"
    DURING = "during"
    AFTER = "after"
    POSTER = "poster"
    GENERAL = "general"


class Album(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "albums"

    club_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)

    club: Mapped["Club"] = relationship(back_populates="albums")
    photos: Mapped[List["Photo"]] = relationship(back_populates="album", cascade="all, delete-orphan")


class Photo(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "photos"

    album_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("albums.id", ondelete="CASCADE"), nullable=False)
    uploaded_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500))
    caption: Mapped[Optional[str]] = mapped_column(String(500))
    tag: Mapped[PhotoTag] = mapped_column(SAEnum(PhotoTag), default=PhotoTag.GENERAL)
    is_cover: Mapped[bool] = mapped_column(Boolean, default=False)

    album: Mapped["Album"] = relationship(back_populates="photos")
