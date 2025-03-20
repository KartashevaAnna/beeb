import random

from sqlalchemy import delete, select

from app.models import Expense
from app.repositories.expenses import ExpensesRepo
from app.utils.constants import PRODUCTS
from app.utils.enums import ExpenseCategory


def test_expenses_default_sorting(client, fill_db, session):
    """Case: normal mode.

    Checks that the latest added expense by default
    will be at the top of the list returned by the repository.
    """
    all_expenses_before_adding = ExpensesRepo(session).read_all()
    expense = Expense(
        name=random.choice(PRODUCTS),
        price=random.randrange(100, 5000, 100),
        category=ExpenseCategory.list_names()[0],
    )
    session.add(expense)
    session.flush()
    session.commit()
    session.expire_all()
    all_expenses_after_adding = ExpensesRepo(session).read_all()
    assert all_expenses_before_adding[0] != all_expenses_after_adding[0]
    assert expense.id == all_expenses_after_adding[0].id
    #  delete the created expense so that it does not convolute further tests
    stmt = delete(Expense).where(Expense.id > 0)
    session.execute(stmt)
    session.commit()
    # check that there are no expenses left in the database
    statement = select(Expense).order_by(Expense.created_at.desc())
    res = session.execute(statement)
    all_expenses = res.scalars().all()
    assert not all_expenses
