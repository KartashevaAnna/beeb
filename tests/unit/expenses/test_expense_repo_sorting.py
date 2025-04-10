import random

from app.models import Expense
from app.repositories.expenses import ExpensesRepo
from app.utils.constants import PRODUCTS


def test_expenses_default_sorting(client, fill_db, category, session):
    """Case: normal mode.

    Checks that the latest added expense by default
    will be at the top of the list returned by the repository.
    """
    all_expenses_before_adding = ExpensesRepo(session).read_all()
    expense = Expense(
        name=random.choice(PRODUCTS),
        price=random.randrange(100, 5000, 100),
        category_id=category.id,
    )
    session.add(expense)
    session.flush()
    session.commit()
    session.expire_all()
    all_expenses_after_adding = ExpensesRepo(session).read_all()
    assert all_expenses_before_adding[0] != all_expenses_after_adding[0]
    assert expense.id == all_expenses_after_adding[0].id
