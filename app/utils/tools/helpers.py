import random

from app.models import Expense
from tests.constants import PRODUCTS


def add_expenses_to_db(session) -> Expense:
    expense = Expense(
        name=random.choice(PRODUCTS),
        price=random.randrange(100, 5000, 100),
    )
    session.add(expense)
    session.commit()
