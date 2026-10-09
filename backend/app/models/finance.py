"""
Module 6: Finance Log
"""
import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Numeric, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from app.models.mixins import UUID, UUIDMixin, TimestampMixin
import enum

if TYPE_CHECKING:
    from app.models.club import Club
    from app.models.event import Event


class BudgetStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


class Budget(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "budgets"

    club_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=False)
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    total_requested: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    total_approved: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    status: Mapped[BudgetStatus] = mapped_column(SAEnum(BudgetStatus), default=BudgetStatus.DRAFT)
    notes: Mapped[Optional[str]] = mapped_column(Text)


class Expense(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "expenses"

    club_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=False)
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=True)
    budget_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("budgets.id"), nullable=True)

    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    receipt_url: Mapped[Optional[str]] = mapped_column(String(500))
    paid_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))


class Income(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "incomes"

    club_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=False)
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=True)

    source: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)
