from typing import List

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session
from sqlalchemy.sql import functions

from app.models import Expense
from app.schemas.expenses import ExpenseCreate, ExpenseShow, ExpenseUpdate
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

    def create(self, expense: ExpenseCreate) -> Expense:
        new_expense = Expense(**expense.model_dump())
        self.session.add(new_expense)
        self.session.commit()
        statement = select(Expense).where(Expense.id == new_expense.id)
        results = self.session.execute(statement)
        expense = results.scalars().one_or_none()
        return expense

    def update(self, expense_id: int, to_upate: ExpenseUpdate):
        stmt = (
            update(Expense)
            .where(Expense.id == expense_id)
            .values(name=to_upate.name, price=to_upate.price_in_kopecks)
        )
        self.session.execute(stmt)
        self.session.commit()

    def delete(self, expense_id: int):
        stmt = delete(Expense).where(Expense.id == expense_id)
        self.session.execute(stmt)
        self.session.commit()
