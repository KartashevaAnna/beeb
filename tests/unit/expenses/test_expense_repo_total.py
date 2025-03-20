import datetime
import random

from sqlalchemy import delete, select

from app.models import Expense
from app.repositories.expenses import ExpensesRepo
from app.utils.constants import PRODUCTS
from app.utils.enums import ExpenseCategory
from app.utils.tools.helpers import get_readable_price


def test_expenses_total(fill_db, session):
    """Case: normal mode.

    Checks that the repo return total expenses correctly.
    """
    statement = select(Expense).order_by(Expense.created_at.desc())
    res = session.execute(statement)
    all_expenses = res.scalars().all()
    total = sum(expense.price for expense in all_expenses)
    assert ExpensesRepo(session).get_total() == get_readable_price(total)


def test_expenses_total_days_no_expenses(session):
    """Case: there are no expenses in database.

    Check that the repo returns 0.
    """
    assert ExpensesRepo(session).get_total_days() == 0


def test_expenses_total_days_just_one_expense(session):
    """Case: there is only one entry in the database.

    Check that the repo returns 0.
    """
    #  add one expense to the database
    expense = Expense(
        name=random.choice(PRODUCTS),
        price=100,
        category=random.choice(ExpenseCategory.list_names()),
        created_at=datetime.datetime.now(),
    )
    session.add(expense)
    session.flush()
    session.commit()
    # check that the repo returns 0.
    assert ExpensesRepo(session).get_total_days() == 0
    #  delete the created expense so that it does not convolute further tests
    stmt = delete(Expense).where(Expense.id > 0)
    session.execute(stmt)
    session.commit()
    # check that there are no expenses left in the database
    statement = select(Expense)
    res = session.execute(statement)
    all_expenses = res.scalars().all()
    assert not all_expenses
