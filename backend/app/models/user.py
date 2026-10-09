"""
Module 2: User Accounts and Profiles
"""
import uuid
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Boolean, ForeignKey, Enum as SAEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from app.models.mixins import UUID, UUIDMixin, TimestampMixin
import enum

if TYPE_CHECKING:
    from app.models.membership import Membership, JoinRequest
    from app.models.notification import Notification


class GlobalRole(str, enum.Enum):
    PLATFORM_ADMIN = "platform_admin"
    FACULTY_COORDINATOR = "faculty_coordinator"
    STUDENT = "student"


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    global_role: Mapped[GlobalRole] = mapped_column(
        SAEnum(GlobalRole), default=GlobalRole.STUDENT
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    profile: Mapped[Optional["UserProfile"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    memberships: Mapped[List["Membership"]] = relationship(back_populates="user")
    join_requests: Mapped[List["JoinRequest"]] = relationship(
        back_populates="user", foreign_keys="JoinRequest.user_id"
    )
    notifications: Mapped[List["Notification"]] = relationship(back_populates="user")


class UserProfile(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    college_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("colleges.id"), nullable=True
    )
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True
    )
    roll_number: Mapped[Optional[str]] = mapped_column(String(50))
    year_of_study: Mapped[Optional[int]] = mapped_column()
    branch: Mapped[Optional[str]] = mapped_column(String(100))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    bio: Mapped[Optional[str]] = mapped_column(Text)
    interests: Mapped[Optional[str]] = mapped_column(Text)   # comma-separated
    skills: Mapped[Optional[str]] = mapped_column(Text)      # comma-separated
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Relationships
    user: Mapped["User"] = relationship(back_populates="profile")
