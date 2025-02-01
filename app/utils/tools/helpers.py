import random

from app.models import Expense
from tests.constants import PRODUCTS


def get_expense(session) -> Expense:
    expense = Expense(
        name=random.choice(PRODUCTS),
        price=random.randrange(100, 5000, 100),
    )
    session.add(expense)
    session.commit()
    return expense
