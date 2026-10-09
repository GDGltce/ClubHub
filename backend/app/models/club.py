"""
Module 1b: Club Model
"""
import uuid
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Text, Boolean, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from app.models.mixins import UUID, UUIDMixin, TimestampMixin
import enum

if TYPE_CHECKING:
    from app.models.institution import College, Department
    from app.models.membership import Membership, JoinRequest, CommitteeTerm
    from app.models.event import Event
    from app.models.document import Document
    from app.models.meeting import Meeting
    from app.models.content import ContentPlan
    from app.models.media import Album


class ClubType(str, enum.Enum):
    DEPARTMENTAL = "departmental"
    INTER_DEPARTMENTAL = "inter_departmental"
    INSTITUTE_LEVEL = "institute_level"


class ClubStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class Club(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "clubs"

    college_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False
    )
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True
    )
    faculty_coordinator_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    short_name: Mapped[Optional[str]] = mapped_column(String(30))
    description: Mapped[Optional[str]] = mapped_column(Text)
    tagline: Mapped[Optional[str]] = mapped_column(String(255))
    club_type: Mapped[ClubType] = mapped_column(SAEnum(ClubType), default=ClubType.DEPARTMENTAL)
    status: Mapped[ClubStatus] = mapped_column(SAEnum(ClubStatus), default=ClubStatus.PENDING)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500))
    cover_url: Mapped[Optional[str]] = mapped_column(String(500))
    instagram_handle: Mapped[Optional[str]] = mapped_column(String(100))
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(255))
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    college: Mapped["College"] = relationship(back_populates="clubs")
    department: Mapped[Optional["Department"]] = relationship(back_populates="clubs")
    memberships: Mapped[List["Membership"]] = relationship(back_populates="club")
    join_requests: Mapped[List["JoinRequest"]] = relationship(back_populates="club")
    committee_terms: Mapped[List["CommitteeTerm"]] = relationship(back_populates="club")
    events: Mapped[List["Event"]] = relationship(back_populates="club")
    documents: Mapped[List["Document"]] = relationship(back_populates="club")
    meetings: Mapped[List["Meeting"]] = relationship(back_populates="club")
    content_plans: Mapped[List["ContentPlan"]] = relationship(back_populates="club")
    albums: Mapped[List["Album"]] = relationship(back_populates="club")
