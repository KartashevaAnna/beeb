from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql import functions

from app.models import Expense
from app.schemas.expenses import ExpenseShow
from app.utils.tools.helpers import get_readable_price


class ExpensesRepo:
    def __init__(self, session: Session) -> None:
        self.session = session

    def read_all(self) -> List[Expense]:
        statement = select(Expense)
        res = self.session.execute(statement)
        results = res.scalars().all()
        return [ExpenseShow(**expense.__dict__) for expense in results]

    def get_total(self) -> int:
        statement = select(functions.sum(Expense.price))
        results = self.session.execute(statement)
        total_numeric = results.scalars().first()
        return get_readable_price(total_numeric) if total_numeric else None

    def read(self, expense_id: int) -> Expense | None:
        statement = select(Expense).where(Expense.id == expense_id)
        results = self.session.execute(statement)
        expense = results.scalars().one_or_none()
        return ExpenseShow(**expense.__dict__) if expense else None
