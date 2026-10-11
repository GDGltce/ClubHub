"""
Module 6: Finance schemas
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
import uuid
from app.models.finance import BudgetStatus

class BudgetCreate(BaseModel):
    club_id: uuid.UUID
    title: str
    event_id: Optional[uuid.UUID] = None
    total_requested: Optional[float] = None
    total_approved: Optional[float] = None
    status: BudgetStatus = BudgetStatus.DRAFT
    notes: Optional[str] = None


class BudgetUpdate(BaseModel):
    title: Optional[str] = None
    event_id: Optional[uuid.UUID] = None
    total_requested: Optional[float] = None
    total_approved: Optional[float] = None
    status: Optional[BudgetStatus] = None
    notes: Optional[str] = None


class BudgetOut(BaseModel):
    id: uuid.UUID
    club_id: uuid.UUID
    event_id: Optional[uuid.UUID] = None
    title: str
    total_requested: Optional[float] = None
    total_approved: Optional[float] = None
    status: BudgetStatus
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ExpenseCreate(BaseModel):
    club_id: uuid.UUID
    description: str
    amount: float
    event_id: Optional[uuid.UUID] = None
    budget_id: Optional[uuid.UUID] = None
    receipt_url: Optional[str] = None
    paid_by_id: Optional[uuid.UUID] = None


class ExpenseUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[float] = None
    event_id: Optional[uuid.UUID] = None
    budget_id: Optional[uuid.UUID] = None
    receipt_url: Optional[str] = None
    paid_by_id: Optional[uuid.UUID] = None


class ExpenseOut(BaseModel):
    id: uuid.UUID
    club_id: uuid.UUID
    event_id: Optional[uuid.UUID] = None
    budget_id: Optional[uuid.UUID] = None
    description: str
    amount: float
    receipt_url: Optional[str] = None
    paid_by_id: Optional[uuid.UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class IncomeCreate(BaseModel):
    club_id: uuid.UUID
    source: str
    amount: float
    event_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None


class IncomeUpdate(BaseModel):
    source: Optional[str] = None
    amount: Optional[float] = None
    event_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None


class IncomeOut(BaseModel):
    id: uuid.UUID
    club_id: uuid.UUID
    event_id: Optional[uuid.UUID] = None
    source: str
    amount: float
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class FinanceSummary(BaseModel):
    club_id: uuid.UUID
    total_requested_budget: float
    total_approved_budget: float
    total_expenses: float
    total_income: float
    net_balance: float
