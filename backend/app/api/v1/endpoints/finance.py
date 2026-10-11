"""
Module 6: Finance Log Endpoints – Budgets, Expenses, Incomes, and Summary
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.models.club import Club
from app.models.event import Event
from app.models.user import User, GlobalRole
from app.models.membership import Membership, ClubRole
from app.models.finance import Budget, Expense, Income, BudgetStatus
from app.schemas.finance import (
    BudgetCreate, BudgetUpdate, BudgetOut,
    ExpenseCreate, ExpenseUpdate, ExpenseOut,
    IncomeCreate, IncomeUpdate, IncomeOut,
    FinanceSummary
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/finance", tags=["Finance"])


def check_finance_access(db: Session, club_id: uuid.UUID, user: User) -> bool:
    """
    Ensure the user is authorized to modify finance records for the club.
    Allowed: Platform Admins, Faculty Coordinators, or Club members with
    TREASURER, PRESIDENT, SECRETARY, or CORE_MEMBER roles.
    """
    if user.global_role in (GlobalRole.PLATFORM_ADMIN, GlobalRole.FACULTY_COORDINATOR):
        return True

    membership = db.query(Membership).filter(
        Membership.club_id == club_id,
        Membership.user_id == user.id,
        Membership.is_active == True
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be an active member of this club to manage finance records"
        )

    allowed_roles = (
        ClubRole.TREASURER,
        ClubRole.PRESIDENT,
        ClubRole.SECRETARY,
        ClubRole.CORE_MEMBER
    )
    if membership.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Treasurer or Club Officer role required to manage finances"
        )

    return True



@router.post("/budgets", response_model=BudgetOut, status_code=status.HTTP_201_CREATED)
def create_budget(
    body: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    club = db.query(Club).filter(Club.id == body.club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    check_finance_access(db, body.club_id, current_user)

    if body.event_id:
        event = db.query(Event).filter(Event.id == body.event_id, Event.club_id == body.club_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found for this club")

    budget = Budget(**body.model_dump())
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


@router.get("/budgets/club/{club_id}", response_model=List[BudgetOut])
def list_club_budgets(
    club_id: uuid.UUID,
    event_id: Optional[uuid.UUID] = Query(None),
    status_filter: Optional[BudgetStatus] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    q = db.query(Budget).filter(Budget.club_id == club_id)
    if event_id:
        q = q.filter(Budget.event_id == event_id)
    if status_filter:
        q = q.filter(Budget.status == status_filter)

    return q.order_by(Budget.created_at.desc()).all()


@router.get("/budgets/{budget_id}", response_model=BudgetOut)
def get_budget(
    budget_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget


@router.patch("/budgets/{budget_id}", response_model=BudgetOut)
def update_budget(
    budget_id: uuid.UUID,
    body: BudgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    check_finance_access(db, budget.club_id, current_user)

    if body.event_id:
        event = db.query(Event).filter(Event.id == body.event_id, Event.club_id == budget.club_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found for this club")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(budget, field, value)

    db.commit()
    db.refresh(budget)
    return budget


@router.delete("/budgets/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    check_finance_access(db, budget.club_id, current_user)

    db.query(Expense).filter(Expense.budget_id == budget_id).update({Expense.budget_id: None})

    db.delete(budget)
    db.commit()
    return None



@router.post("/expenses", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
def create_expense(
    body: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    club = db.query(Club).filter(Club.id == body.club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    check_finance_access(db, body.club_id, current_user)

    if body.budget_id:
        budget = db.query(Budget).filter(Budget.id == body.budget_id, Budget.club_id == body.club_id).first()
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found for this club")

    if body.event_id:
        event = db.query(Event).filter(Event.id == body.event_id, Event.club_id == body.club_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found for this club")

    expense_data = body.model_dump()
    if expense_data.get("paid_by_id") is None:
        expense_data["paid_by_id"] = current_user.id

    expense = Expense(**expense_data)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.get("/expenses/club/{club_id}", response_model=List[ExpenseOut])
def list_club_expenses(
    club_id: uuid.UUID,
    budget_id: Optional[uuid.UUID] = Query(None),
    event_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    q = db.query(Expense).filter(Expense.club_id == club_id)
    if budget_id:
        q = q.filter(Expense.budget_id == budget_id)
    if event_id:
        q = q.filter(Expense.event_id == event_id)

    return q.order_by(Expense.created_at.desc()).all()


@router.get("/expenses/{expense_id}", response_model=ExpenseOut)
def get_expense(
    expense_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.patch("/expenses/{expense_id}", response_model=ExpenseOut)
def update_expense(
    expense_id: uuid.UUID,
    body: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    check_finance_access(db, expense.club_id, current_user)

    if body.budget_id:
        budget = db.query(Budget).filter(Budget.id == body.budget_id, Budget.club_id == expense.club_id).first()
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found for this club")

    if body.event_id:
        event = db.query(Event).filter(Event.id == body.event_id, Event.club_id == expense.club_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found for this club")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(expense, field, value)

    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    check_finance_access(db, expense.club_id, current_user)

    db.delete(expense)
    db.commit()
    return None



@router.post("/incomes", response_model=IncomeOut, status_code=status.HTTP_201_CREATED)
def create_income(
    body: IncomeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    club = db.query(Club).filter(Club.id == body.club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    check_finance_access(db, body.club_id, current_user)

    if body.event_id:
        event = db.query(Event).filter(Event.id == body.event_id, Event.club_id == body.club_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found for this club")

    income = Income(**body.model_dump())
    db.add(income)
    db.commit()
    db.refresh(income)
    return income


@router.get("/incomes/club/{club_id}", response_model=List[IncomeOut])
def list_club_incomes(
    club_id: uuid.UUID,
    event_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    q = db.query(Income).filter(Income.club_id == club_id)
    if event_id:
        q = q.filter(Income.event_id == event_id)

    return q.order_by(Income.created_at.desc()).all()


@router.get("/incomes/{income_id}", response_model=IncomeOut)
def get_income(
    income_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    income = db.query(Income).filter(Income.id == income_id).first()
    if not income:
        raise HTTPException(status_code=404, detail="Income not found")
    return income


@router.patch("/incomes/{income_id}", response_model=IncomeOut)
def update_income(
    income_id: uuid.UUID,
    body: IncomeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    income = db.query(Income).filter(Income.id == income_id).first()
    if not income:
        raise HTTPException(status_code=404, detail="Income not found")

    check_finance_access(db, income.club_id, current_user)

    if body.event_id:
        event = db.query(Event).filter(Event.id == body.event_id, Event.club_id == income.club_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found for this club")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(income, field, value)

    db.commit()
    db.refresh(income)
    return income


@router.delete("/incomes/{income_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_income(
    income_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    income = db.query(Income).filter(Income.id == income_id).first()
    if not income:
        raise HTTPException(status_code=404, detail="Income not found")

    check_finance_access(db, income.club_id, current_user)

    db.delete(income)
    db.commit()
    return None



@router.get("/summary/club/{club_id}", response_model=FinanceSummary)
def get_club_finance_summary(
    club_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    budgets = db.query(Budget).filter(Budget.club_id == club_id).all()
    expenses = db.query(Expense).filter(Expense.club_id == club_id).all()
    incomes = db.query(Income).filter(Income.club_id == club_id).all()

    total_requested = sum(float(b.total_requested or 0) for b in budgets)
    total_approved = sum(float(b.total_approved or 0) for b in budgets if b.status == BudgetStatus.APPROVED)
    total_exp = sum(float(e.amount or 0) for e in expenses)
    total_inc = sum(float(i.amount or 0) for i in incomes)
    net_bal = round(total_inc - total_exp, 2)

    return FinanceSummary(
        club_id=club_id,
        total_requested_budget=round(total_requested, 2),
        total_approved_budget=round(total_approved, 2),
        total_expenses=round(total_exp, 2),
        total_income=round(total_inc, 2),
        net_balance=net_bal
    )
