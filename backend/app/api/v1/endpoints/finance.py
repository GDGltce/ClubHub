"""Club finance endpoints with club-scoped authorization."""
from decimal import Decimal
from typing import TypeVar
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.finance import Budget, BudgetStatus, Expense, Income
from app.models.membership import ClubRole, Membership
from app.models.user import GlobalRole, User
from app.schemas.finance import (
    BudgetCreate, BudgetUpdate, BudgetOut,
    ExpenseCreate, ExpenseUpdate, ExpenseOut,
    IncomeCreate, IncomeUpdate, IncomeOut,
    FinanceSummary,
)

router = APIRouter(prefix="/finance", tags=["Finance"])

OFFICER_ROLES = {
    ClubRole.PRESIDENT,
    ClubRole.TREASURER,
    ClubRole.SECRETARY,
    ClubRole.CORE_MEMBER,
}


def _can_read(club_id: uuid.UUID, user: User, db: Session) -> bool:
    if user.global_role in {
        GlobalRole.PLATFORM_ADMIN,
        GlobalRole.FACULTY_COORDINATOR,
    }:
        return True
    return db.query(Membership.id).filter(
        Membership.club_id == club_id,
        Membership.user_id == user.id,
        Membership.is_active.is_(True),
    ).first() is not None


def _can_manage(club_id: uuid.UUID, user: User, db: Session) -> bool:
    if user.global_role == GlobalRole.PLATFORM_ADMIN:
        return True
    return db.query(Membership.id).filter(
        Membership.club_id == club_id,
        Membership.user_id == user.id,
        Membership.is_active.is_(True),
        Membership.role.in_(OFFICER_ROLES),
    ).first() is not None


def _require_read(club_id: uuid.UUID, user: User, db: Session) -> None:
    if not _can_read(club_id, user, db):
        raise HTTPException(status_code=403, detail="Club membership required")


def _require_manage(club_id: uuid.UUID, user: User, db: Session) -> None:
    if not _can_manage(club_id, user, db):
        raise HTTPException(status_code=403, detail="Club officer access required")


def _validate_event(club_id: uuid.UUID, event_id: uuid.UUID | None, db: Session) -> None:
    if event_id is None:
        return
    from app.models.event import Event
    exists = db.query(Event.id).filter(
        Event.id == event_id,
        Event.club_id == club_id,
    ).first()
    if not exists:
        raise HTTPException(status_code=422, detail="Event does not belong to this club")


def _get_or_404(model, record_id: uuid.UUID, db: Session):
    record = db.query(model).filter(model.id == record_id).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Finance record not found")
    return record


def _save(db: Session, record):
    try:
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    except Exception:
        db.rollback()
        raise


@router.post("/budgets", response_model=BudgetOut, status_code=status.HTTP_201_CREATED)
def create_budget(
    payload: BudgetCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _require_manage(payload.club_id, user, db)
    _validate_event(payload.club_id, payload.event_id, db)
    record = Budget(**payload.model_dump())
    return _save(db, record)


@router.get("/budgets", response_model=list[BudgetOut])
def list_budgets(
    club_id: uuid.UUID = Query(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _require_read(club_id, user, db)
    return db.query(Budget).filter(Budget.club_id == club_id).order_by(Budget.created_at.desc()).all()


@router.get("/budgets/{record_id}", response_model=BudgetOut)
def get_budget(
    record_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    record = _get_or_404(Budget, record_id, db)
    _require_read(record.club_id, user, db)
    return record


@router.patch("/budgets/{record_id}", response_model=BudgetOut)
def update_budget(
    record_id: uuid.UUID,
    payload: BudgetUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    record = _get_or_404(Budget, record_id, db)
    _require_manage(record.club_id, user, db)
    changes = payload.model_dump(exclude_unset=True)
    _validate_event(record.club_id, changes.get("event_id", record.event_id), db)
    for key, value in changes.items():
        setattr(record, key, value)
    return _save(db, record)


@router.delete("/budgets/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    record_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    record = _get_or_404(Budget, record_id, db)
    _require_manage(record.club_id, user, db)
    db.delete(record)
    db.commit()


@router.post("/expenses", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
def create_expense(
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _require_manage(payload.club_id, user, db)
    _validate_event(payload.club_id, payload.event_id, db)
    if payload.budget_id:
        budget = _get_or_404(Budget, payload.budget_id, db)
        if budget.club_id != payload.club_id:
            raise HTTPException(status_code=422, detail="Budget does not belong to this club")
    record = Expense(**payload.model_dump(), paid_by_id=user.id)
    return _save(db, record)


@router.get("/expenses", response_model=list[ExpenseOut])
def list_expenses(
    club_id: uuid.UUID = Query(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _require_read(club_id, user, db)
    return db.query(Expense).filter(Expense.club_id == club_id).order_by(Expense.created_at.desc()).all()


@router.get("/expenses/{record_id}", response_model=ExpenseOut)
def get_expense(
    record_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    record = _get_or_404(Expense, record_id, db)
    _require_read(record.club_id, user, db)
    return record


@router.patch("/expenses/{record_id}", response_model=ExpenseOut)
def update_expense(
    record_id: uuid.UUID,
    payload: ExpenseUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    record = _get_or_404(Expense, record_id, db)
    _require_manage(record.club_id, user, db)
    changes = payload.model_dump(exclude_unset=True)
    _validate_event(record.club_id, changes.get("event_id", record.event_id), db)
    budget_id = changes.get("budget_id", record.budget_id)
    if budget_id:
        budget = _get_or_404(Budget, budget_id, db)
        if budget.club_id != record.club_id:
            raise HTTPException(status_code=422, detail="Budget does not belong to this club")
    for key, value in changes.items():
        setattr(record, key, value)
    return _save(db, record)


@router.delete("/expenses/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    record_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    record = _get_or_404(Expense, record_id, db)
    _require_manage(record.club_id, user, db)
    db.delete(record)
    db.commit()


@router.post("/incomes", response_model=IncomeOut, status_code=status.HTTP_201_CREATED)
def create_income(
    payload: IncomeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _require_manage(payload.club_id, user, db)
    _validate_event(payload.club_id, payload.event_id, db)
    return _save(db, Income(**payload.model_dump()))


@router.get("/incomes", response_model=list[IncomeOut])
def list_incomes(
    club_id: uuid.UUID = Query(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _require_read(club_id, user, db)
    return db.query(Income).filter(Income.club_id == club_id).order_by(Income.created_at.desc()).all()


@router.get("/incomes/{record_id}", response_model=IncomeOut)
def get_income(
    record_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    record = _get_or_404(Income, record_id, db)
    _require_read(record.club_id, user, db)
    return record


@router.patch("/incomes/{record_id}", response_model=IncomeOut)
def update_income(
    record_id: uuid.UUID,
    payload: IncomeUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    record = _get_or_404(Income, record_id, db)
    _require_manage(record.club_id, user, db)
    changes = payload.model_dump(exclude_unset=True)
    _validate_event(record.club_id, changes.get("event_id", record.event_id), db)
    for key, value in changes.items():
        setattr(record, key, value)
    return _save(db, record)


@router.delete("/incomes/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_income(
    record_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    record = _get_or_404(Income, record_id, db)
    _require_manage(record.club_id, user, db)
    db.delete(record)
    db.commit()


@router.get("/summary", response_model=FinanceSummary)
def finance_summary(
    club_id: uuid.UUID = Query(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _require_read(club_id, user, db)
    total_income = db.query(func.coalesce(func.sum(Income.amount), 0)).filter(
        Income.club_id == club_id
    ).scalar()
    total_expenses = db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
        Expense.club_id == club_id
    ).scalar()
    budget_count = db.query(func.count(Budget.id)).filter(
        Budget.club_id == club_id
    ).scalar()
    income = Decimal(str(total_income))
    expenses = Decimal(str(total_expenses))
    return FinanceSummary(
        club_id=club_id,
        total_income=income,
        total_expenses=expenses,
        balance=income - expenses,
        budget_count=budget_count or 0,
    )
