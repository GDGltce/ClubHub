"""
Module 11: Notifications
"""
import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Boolean, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from app.models.mixins import UUID, UUIDMixin, TimestampMixin
import enum

if TYPE_CHECKING:
    from app.models.user import User


class NotificationType(str, enum.Enum):
    JOIN_REQUEST = "join_request"
    JOIN_APPROVED = "join_approved"
    JOIN_REJECTED = "join_rejected"
    EVENT_CREATED = "event_created"
    EVENT_REMINDER = "event_reminder"
    DOCUMENT_APPROVED = "document_approved"
    TASK_ASSIGNED = "task_assigned"
    MEETING_SCHEDULED = "meeting_scheduled"
    GENERAL = "general"


class Notification(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "notifications"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[NotificationType] = mapped_column(SAEnum(NotificationType), default=NotificationType.GENERAL)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[Optional[str]] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    related_entity_type: Mapped[Optional[str]] = mapped_column(String(50))  # "event", "club", etc.
    related_entity_id: Mapped[Optional[str]] = mapped_column(String(50))

    user: Mapped["User"] = relationship(back_populates="notifications")
