import datetime

from app.utils.tools.helpers import get_monthly_expenses
from tests.conftest import add_expense, get_expenses


def test_get_monthly_expenses(session, category):
    """Case: normal mode. Verify monthly expenses.

    Checks that the helper function called by the repo
    correctly adds up monthly expenses.
    """
    # create three expenses: 1 for current month and 2 for the previous month
    first_expense = add_expense(
        session=session,
        price=100,
        category_id=category.id,
        created_at=datetime.datetime.now(),
    )
    second_expense = add_expense(
        session=session,
        price=400,
        category_id=category.id,
        created_at=datetime.datetime.now() - datetime.timedelta(weeks=-4),
    )
    third_expense = add_expense(
        session=session,
        price=200,
        category_id=category.id,
        created_at=datetime.datetime.now() - datetime.timedelta(weeks=-4),
    )
    session.commit()
    # get a list of all created expenses and pass it to the helper function
    all_expenses = get_expenses(session)
    # get a response from the helper function adding up expenses
    monthly_breakdown = get_monthly_expenses(all_expenses)
    assert (
        monthly_breakdown[first_expense.created_at.strftime("%m")]
        == first_expense.price
    )
    assert (
        monthly_breakdown[second_expense.created_at.strftime("%m")]
        == second_expense.price + third_expense.price
    )
