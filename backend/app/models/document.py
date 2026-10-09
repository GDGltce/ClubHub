"""
Module 5: Document Vault
"""
import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Boolean, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from app.models.mixins import UUID, UUIDMixin, TimestampMixin
import enum

if TYPE_CHECKING:
    from app.models.club import Club
    from app.models.event import Event


class DocumentCategory(str, enum.Enum):
    PERMISSION_LETTER = "permission_letter"
    BUDGET_SHEET = "budget_sheet"
    INVOICE = "invoice"
    SPONSORSHIP = "sponsorship"
    MOU = "mou"
    REPORT = "report"
    MINUTES = "minutes"
    OTHER = "other"


class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Document(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "documents"

    club_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=True)
    uploaded_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    approved_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[DocumentCategory] = mapped_column(SAEnum(DocumentCategory), default=DocumentCategory.OTHER)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[Optional[str]] = mapped_column(String(255))
    file_size_bytes: Mapped[Optional[int]] = mapped_column()
    version: Mapped[int] = mapped_column(default=1)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    approval_status: Mapped[ApprovalStatus] = mapped_column(SAEnum(ApprovalStatus), default=ApprovalStatus.PENDING)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)

    club: Mapped["Club"] = relationship(back_populates="documents")
    event: Mapped[Optional["Event"]] = relationship(back_populates="documents")
