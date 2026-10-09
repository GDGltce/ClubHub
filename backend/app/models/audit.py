"""
Module 12: Audit Trail – Activity Log
"""
import uuid
from typing import Optional
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base
from app.models.mixins import UUID, UUIDMixin, TimestampMixin


class ActivityLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "activity_logs"

    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)   # e.g. "event.stage_change"
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "event", "club", etc.
    entity_id: Mapped[Optional[str]] = mapped_column(String(50))
    detail: Mapped[Optional[str]] = mapped_column(Text)  # JSON string with before/after
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
