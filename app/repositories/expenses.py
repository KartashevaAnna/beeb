from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Expense


class ExpenseRepo:
    def __init__(self, session: Session) -> None:
        self.session = session

    def read_all(self) -> list[Expense]:
        statement = select(Expense)
        results = self.session.execute(statement)
        return results.scalars().all()
