import datetime
from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session

from app.exceptions import IncomeNotFoundError, NotOwnerError
from app.models import Income
from app.schemas.dates import DateFilter
from app.schemas.income import IncomeCreate, IncomeShowOne, IncomeUpdate


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
        income = results.scalars().all()
        if not income:
            raise IncomeNotFoundError(income_id)
        return IncomeShowOne(**income[0].__dict__)

    def delete(self, income_id: int, user_id: int):
        old_income = self.read(income_id)
        if old_income.user_id != user_id:
            raise NotOwnerError(old_income.name)
        statement = delete(Income).where(Income.id == income_id)
        self.session.execute(statement)
        self.session.commit()

    def update(self, income_id: int, user_id: int, to_update: IncomeUpdate):
        old_income = self.read(income_id)
        if old_income.user_id != user_id:
            raise NotOwnerError(old_income.name)
        statement = (
            update(Income)
            .where(Income.id == income_id)
            .values(
                name=to_update.name,
                amount=to_update.amount,
                created_at=to_update.created_at,
            )
        )
        self.session.execute(statement)
        self.session.commit()

    def read_all(self, user_id: int) -> list[Income]:
        statement = select(Income).where(Income.user_id == user_id)
        results = self.session.execute(statement)
        return results.scalars().all()

    def sum_income(self, user_id: int, max_date: datetime.datetime) -> int:
        income_sum = (
            self.session.query(func.sum(Income.amount))
            .where(Income.user_id == user_id)
            .where(Income.created_at <= max_date)
            .scalar()
        )
        return income_sum if income_sum else 0
