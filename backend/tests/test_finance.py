from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock
import uuid

import pytest
from pydantic import ValidationError

from app.api.v1.endpoints.finance import _can_manage, _can_read
from app.models.membership import ClubRole
from app.models.user import GlobalRole
from app.schemas.finance import BudgetCreate, ExpenseCreate, IncomeCreate


def test_budget_requires_title():
    with pytest.raises(ValidationError):
        BudgetCreate(club_id=uuid.uuid4(), title="")


@pytest.mark.parametrize("amount", ["0", "-1", "0.001"])
def test_expense_rejects_invalid_amount(amount):
    with pytest.raises(ValidationError):
        ExpenseCreate(
            club_id=uuid.uuid4(),
            description="Stationery",
            amount=amount,
        )


def test_income_accepts_positive_decimal_amount():
    income = IncomeCreate(
        club_id=uuid.uuid4(),
        source="Sponsorship",
        amount="1500.50",
    )
    assert income.amount == Decimal("1500.50")


def test_platform_admin_can_manage_without_membership():
    user = SimpleNamespace(
        id=uuid.uuid4(),
        global_role=GlobalRole.PLATFORM_ADMIN,
    )
    db = MagicMock()

    assert _can_manage(uuid.uuid4(), user, db) is True
    db.query.assert_not_called()


def test_faculty_coordinator_can_read():
    user = SimpleNamespace(
        id=uuid.uuid4(),
        global_role=GlobalRole.FACULTY_COORDINATOR,
    )
    assert _can_read(uuid.uuid4(), user, MagicMock()) is True


def test_active_club_officer_can_manage():
    user = SimpleNamespace(
        id=uuid.uuid4(),
        global_role=GlobalRole.STUDENT,
    )
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = (uuid.uuid4(),)

    assert _can_manage(uuid.uuid4(), user, db) is True


def test_non_member_cannot_manage():
    user = SimpleNamespace(
        id=uuid.uuid4(),
        global_role=GlobalRole.STUDENT,
    )
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    assert _can_manage(uuid.uuid4(), user, db) is False


def test_active_club_member_can_read():
    user = SimpleNamespace(
        id=uuid.uuid4(),
        global_role=GlobalRole.STUDENT,
    )
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = (uuid.uuid4(),)

    assert _can_read(uuid.uuid4(), user, db) is True


def test_non_member_cannot_read():
    user = SimpleNamespace(
        id=uuid.uuid4(),
        global_role=GlobalRole.STUDENT,
    )
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    assert _can_read(uuid.uuid4(), user, db) is False
def test_faculty_coordinator_cannot_manage_without_officer_membership():
    user = SimpleNamespace(
        id=uuid.uuid4(),
        global_role=GlobalRole.FACULTY_COORDINATOR,
    )
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    assert _can_manage(uuid.uuid4(), user, db) is False


def test_finance_patch_rejects_null_required_fields():
    import pytest
    from pydantic import ValidationError
    from app.schemas.finance import BudgetUpdate, ExpenseUpdate, IncomeUpdate

    invalid_payloads = [
        (BudgetUpdate, {"title": None}),
        (BudgetUpdate, {"status": None}),
        (ExpenseUpdate, {"description": None}),
        (ExpenseUpdate, {"amount": None}),
        (IncomeUpdate, {"source": None}),
        (IncomeUpdate, {"amount": None}),
    ]

    for schema, payload in invalid_payloads:
        with pytest.raises(ValidationError):
            schema(**payload)


def test_finance_patch_allows_partial_updates_and_nullable_fields():
    from app.schemas.finance import BudgetUpdate, ExpenseUpdate, IncomeUpdate

    assert BudgetUpdate(notes="Updated").notes == "Updated"
    assert ExpenseUpdate(receipt_url=None).receipt_url is None
    assert IncomeUpdate(notes="Updated").notes == "Updated"
