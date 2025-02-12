from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql import functions

from app.models import Expense


class ExpensesRepo:
    def __init__(self, session: Session) -> None:
        self.session = session

    def read_all(self) -> List[Expense]:
        statement = select(Expense)
        results = self.session.execute(statement)
        return results.scalars().all()

    def get_total(self) -> int:
        statement = select(functions.sum(Expense.price))
        results = self.session.execute(statement)
        return results.scalars().first()

    def read(self, expense_id: int) -> Expense | None:
        statement = select(Expense).where(Expense.id == expense_id)
        results = self.session.execute(statement)
        return results.scalars().one_or_none()
