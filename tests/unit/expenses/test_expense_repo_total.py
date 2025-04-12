from app.repositories.expenses import ExpenseRepo
from app.utils.tools.helpers import get_readable_price
from tests.conftest import get_expenses


def test_expenses_total(fill_db, session):
    """Case: normal mode.

    Checks that the repo return total expenses correctly.
    """
    all_expenses = get_expenses(session)
    total = sum(expense.price for expense in all_expenses)
    assert ExpenseRepo(session).get_total() == get_readable_price(total)


def test_expenses_total_days_no_expenses(session):
    """Case: there are no expenses in database.

    Check that the repo returns 0.
    """
    assert ExpenseRepo(session).get_total_days() == 0


def test_expenses_total_days_just_one_expense(session, category):
    """Case: there is only one entry in the database.

    Check that the repo returns 0.
    """
    assert ExpenseRepo(session).get_total_days() == 0
