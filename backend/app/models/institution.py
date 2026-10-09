"""
Module 1: Institution and Club Registry Models
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
    from app.models.user import User


class CollegeStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"


class College(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "colleges"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    short_name: Mapped[Optional[str]] = mapped_column(String(20))
    university: Mapped[Optional[str]] = mapped_column(String(255))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(100))
    website: Mapped[Optional[str]] = mapped_column(String(255))
    logo_url: Mapped[Optional[str]] = mapped_column(String(500))
    status: Mapped[CollegeStatus] = mapped_column(
        SAEnum(CollegeStatus), default=CollegeStatus.PENDING
    )

    # Relationships
    departments: Mapped[List["Department"]] = relationship(back_populates="college", cascade="all, delete-orphan")
    clubs: Mapped[List["Club"]] = relationship(back_populates="college")


class Department(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "departments"

    college_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    short_name: Mapped[Optional[str]] = mapped_column(String(20))

    # Relationships
    college: Mapped["College"] = relationship(back_populates="departments")
    clubs: Mapped[List["Club"]] = relationship(back_populates="department")
