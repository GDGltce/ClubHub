"""Validated request and response schemas for club finance."""
import uuid
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.finance import BudgetStatus


class BudgetCreate(BaseModel):
    club_id: uuid.UUID
    event_id: Optional[uuid.UUID] = None
    title: str = Field(min_length=1, max_length=255)
    total_requested: Optional[Decimal] = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    notes: Optional[str] = None


class BudgetUpdate(BaseModel):
    event_id: Optional[uuid.UUID] = None
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    total_requested: Optional[Decimal] = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    total_approved: Optional[Decimal] = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    status: Optional[BudgetStatus] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def reject_null_required_fields(self):
        for name in ("title", "status"):
            if name in self.model_fields_set and getattr(self, name) is None:
                raise ValueError(f"{name} cannot be null")
        return self


class BudgetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    club_id: uuid.UUID
    event_id: Optional[uuid.UUID]
    title: str
    total_requested: Optional[Decimal]
    total_approved: Optional[Decimal]
    status: BudgetStatus
    notes: Optional[str]


class ExpenseCreate(BaseModel):
    club_id: uuid.UUID
    event_id: Optional[uuid.UUID] = None
    budget_id: Optional[uuid.UUID] = None
    description: str = Field(min_length=1, max_length=255)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    receipt_url: Optional[str] = Field(default=None, max_length=500)


class ExpenseUpdate(BaseModel):
    event_id: Optional[uuid.UUID] = None
    budget_id: Optional[uuid.UUID] = None
    description: Optional[str] = Field(default=None, min_length=1, max_length=255)
    amount: Optional[Decimal] = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    receipt_url: Optional[str] = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def reject_null_required_fields(self):
        for name in ("description", "amount"):
            if name in self.model_fields_set and getattr(self, name) is None:
                raise ValueError(f"{name} cannot be null")
        return self


class ExpenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    club_id: uuid.UUID
    event_id: Optional[uuid.UUID]
    budget_id: Optional[uuid.UUID]
    description: str
    amount: Decimal
    receipt_url: Optional[str]
    paid_by_id: Optional[uuid.UUID]


class IncomeCreate(BaseModel):
    club_id: uuid.UUID
    event_id: Optional[uuid.UUID] = None
    source: str = Field(min_length=1, max_length=255)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    notes: Optional[str] = None


class IncomeUpdate(BaseModel):
    event_id: Optional[uuid.UUID] = None
    source: Optional[str] = Field(default=None, min_length=1, max_length=255)
    amount: Optional[Decimal] = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    notes: Optional[str] = None

    @model_validator(mode="after")
    def reject_null_required_fields(self):
        for name in ("source", "amount"):
            if name in self.model_fields_set and getattr(self, name) is None:
                raise ValueError(f"{name} cannot be null")
        return self


class IncomeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    club_id: uuid.UUID
    event_id: Optional[uuid.UUID]
    source: str
    amount: Decimal
    notes: Optional[str]


class FinanceSummary(BaseModel):
    club_id: uuid.UUID
    total_income: Decimal
    total_expenses: Decimal
    balance: Decimal
    budget_count: int
