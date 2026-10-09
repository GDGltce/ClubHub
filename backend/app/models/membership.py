"""
Module 3: Membership – join requests, roles, committee terms
"""
import uuid
from typing import Optional, List, TYPE_CHECKING
from datetime import date
from sqlalchemy import String, Text, Boolean, ForeignKey, Date, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from app.models.mixins import UUID, UUIDMixin, TimestampMixin
import enum

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.club import Club


class JoinRequestStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ClubRole(str, enum.Enum):
    PRESIDENT = "president"
    SECRETARY = "secretary"
    TREASURER = "treasurer"
    CORE_MEMBER = "core_member"
    MEMBER = "member"


class JoinRequest(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "join_requests"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    club_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=False)
    motivation: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[JoinRequestStatus] = mapped_column(SAEnum(JoinRequestStatus), default=JoinRequestStatus.PENDING)
    reviewed_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    review_note: Mapped[Optional[str]] = mapped_column(Text)

    user: Mapped["User"] = relationship(back_populates="join_requests", foreign_keys=[user_id])
    club: Mapped["Club"] = relationship(back_populates="join_requests")


class Membership(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "memberships"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    club_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=False)
    role: Mapped[ClubRole] = mapped_column(SAEnum(ClubRole), default=ClubRole.MEMBER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    joined_at: Mapped[Optional[date]] = mapped_column(Date)
    left_at: Mapped[Optional[date]] = mapped_column(Date)

    user: Mapped["User"] = relationship(back_populates="memberships")
    club: Mapped["Club"] = relationship(back_populates="memberships")


class CommitteeTerm(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "committee_terms"

    club_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=False)
    academic_year: Mapped[str] = mapped_column(String(20), nullable=False)  # e.g. "2025-26"
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    club: Mapped["Club"] = relationship(back_populates="committee_terms")
