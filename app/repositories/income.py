from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.exceptions import NotOwnerError
from app.models import Income
from app.schemas.income import IncomeCreate


class IncomeRepo:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, income: IncomeCreate, user_id: int) -> Income:
        new_income = Income(**income.model_dump())
        self.session.add(new_income)
        self.session.commit()
        statement = select(Income).where(Income.id == new_income.id)
        results = self.session.execute(statement)
        return results.scalars().one_or_none()

    def read(self, income_id: int) -> Income | None:
        statement = select(Income).where(Income.id == income_id)
        results = self.session.execute(statement)
        return results.scalars().all()

    def delete(self, income_id: int, user_id: int):
        # old_income = self.read(income_id)
        # if old_income.user_id != user_id:
        #     raise NotOwnerError(old_income.name)
        stmt = delete(Income).where(Income.id == income_id)
        self.session.execute(stmt)
        self.session.commit()
