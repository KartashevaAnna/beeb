import datetime
import random

from sqlalchemy import delete, select

from app.models import Expense
from app.utils.constants import PRODUCTS
from app.utils.enums import ExpenseCategory
from app.utils.tools.helpers import get_monthly_expenses


def test_get_monthly_expenses(session):
    """Case: normal mode. Verify monthly expenses.

    Checks that the helper function called by the repo
    correctly adds up monthly expenses.
    """
    # create three expenses: 1 for current month and 2 for the previous month
    first_expense = Expense(
        name=random.choice(PRODUCTS),
        price=100,
        category=random.choice(ExpenseCategory.list_names()),
        created_at=datetime.datetime.now(),
    )
    session.add(first_expense)
    session.flush()
    second_expense = Expense(
        name=random.choice(PRODUCTS),
        price=400,
        category=random.choice(ExpenseCategory.list_names()),
        created_at=datetime.datetime.now() - datetime.timedelta(weeks=-4),
    )
    session.add(second_expense)
    session.flush()
    third_expense = Expense(
        name=random.choice(PRODUCTS),
        price=200,
        category=random.choice(ExpenseCategory.list_names()),
        created_at=datetime.datetime.now() - datetime.timedelta(weeks=-4),
    )
    session.add(third_expense)
    session.flush()
    session.commit()
    # get a list of all created expenses and pass it to the helper function
    statement = select(Expense).order_by(Expense.created_at.desc())
    res = session.execute(statement)
    all_expenses = res.scalars().all()
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
    #  delete the created expense so that it does not convolute further tests
    stmt = delete(Expense).where(Expense.id > 0)
    session.execute(stmt)
    session.commit()
    # check that there are no expenses left in the database
    statement = select(Expense).order_by(Expense.created_at.desc())
    res = session.execute(statement)
    all_expenses = res.scalars().all()
    assert not all_expenses
