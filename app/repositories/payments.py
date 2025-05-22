import calendar
import datetime

from fastapi import Request
from sqlalchemy import delete, extract, func, select, update
from sqlalchemy.orm import Session

from app.exceptions import NotOwnerError
from app.models import Category, Payment
from app.schemas.dates import DateFilter
from app.schemas.payments import (
    PaymentCreate,
    PaymentShow,
    PaymentShowOne,
    PaymentUpdate,
)
from app.utils.constants import INT_TO_MONTHES, MONTHES
from app.utils.tools.category_helpers import (
    get_payments_shares,
    get_payments_sums_per_category,
    sort_payment_shares,
)
from app.utils.tools.helpers import get_monthly_payments, get_readable_price


class PaymentRepo:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_all_payments(self, user_id: int) -> list[Payment]:
        statement = (
            select(Payment, Category.name)
            .where(Payment.user_id == user_id)
            .join(Payment.payment_category)
            .order_by(Payment.created_at.desc())
        )
        res = self.session.execute(statement)
        return res.scalars().all()

    def get_spendings(self, payments: list[Payment]) -> list[Payment]:
        return [payment for payment in payments if payment.is_spending is True]

    def get_all_incomes(self, payments: list[Payment]) -> list[Payment]:
        return [payment for payment in payments if payment.is_spending is False]

    def get_total_amounts(self, payments: list[Payment]) -> int:
        amount = self.get_total(payments)
        return amount if amount is not None else 0

    def get_days_left(
        self, available_amount: int, total_per_day: int | None = None
    ):
        if not total_per_day:
            return None
        return int(available_amount / total_per_day)

    def get_payments_per_year(self, year: int, user_id: int) -> list[Payment]:
        statement = (
            select(Payment)
            .where(Payment.user_id == user_id)
            .filter(extract("year", Payment.created_at) == year)
        )
        res = self.session.execute(statement)
        return res.scalars().all()

    def get_payments_per_month(
        self, year: int, month: int, user_id: int
    ) -> list[Payment]:
        statement = (
            select(Payment)
            .where(Payment.user_id == user_id)
            .filter(extract("year", Payment.created_at) == year)
            .filter(extract("month", Payment.created_at) == month)
        )
        res = self.session.execute(statement)
        return res.scalars().all()

    def get_payments_per_year_with_category(
        self, year: int, user_id: int
    ) -> list[Payment]:
        statement = (
            select(Payment)
            .where(Payment.user_id == user_id)
            .join(Payment.payment_category)
            .filter(extract("year", Payment.created_at) == year)
        )
        res = self.session.execute(statement)
        return res.scalars().all()

    def read_all(self, user_id: int) -> list[Payment]:
        results = self.get_all_payments(user_id)
        return [
            PaymentShow(
                **payment.__dict__, category=payment.payment_category.name
            )
            for payment in results
        ]

    def get_total(self, payments: list[Payment]) -> int:
        return self.sum_payments_prices(payments)

    def sum_payments_prices(self, payments):
        all_values = [x.price for x in payments]
        result = sum(all_values)
        return result if result else 0

    def get_max_date(
        self, limit: DateFilter, user_id: int
    ) -> datetime.datetime:
        if not limit.year and not limit.month:
            return self.session.scalar(
                select(func.max(Payment.created_at)).where(
                    Payment.user_id == user_id
                )
            )
        if limit.year and not limit.month:
            return self.session.scalar(
                select(func.max(Payment.created_at))
                .where(Payment.user_id == user_id)
                .filter(extract("year", Payment.created_at) == limit.year)
            )
        return self.session.scalar(
            select(func.max(Payment.created_at))
            .where(Payment.user_id == user_id)
            .filter(extract("year", Payment.created_at) == limit.year)
            .filter(extract("month", Payment.created_at) == limit.month)
        )

    def get_min_date(
        self, limit: DateFilter, user_id: int
    ) -> datetime.datetime:
        if not limit.year and not limit.month:
            return self.session.scalar(
                select(func.min(Payment.created_at)).where(
                    Payment.user_id == user_id
                )
            )
        if limit.year and not limit.month:
            return self.session.scalar(
                select(func.min(Payment.created_at))
                .where(Payment.user_id == user_id)
                .filter(extract("year", Payment.created_at) == limit.year)
            )
        return self.session.scalar(
            select(func.min(Payment.created_at))
            .where(Payment.user_id == user_id)
            .filter(extract("year", Payment.created_at) == limit.year)
            .filter(extract("month", Payment.created_at) == limit.month)
        )

    def get_total_days(
        self, max_date: datetime.datetime, min_date: datetime.datetime
    ) -> int:
        if not any([max_date, min_date]):
            return 0
        else:
            delta = max_date - min_date
            return delta.days + 1

    def get_total_per_day(self, total: int, total_days: int) -> int:
        try:
            return total / total_days
        except ZeroDivisionError:
            return total

    def get_monthly_payments(
        self, payments: list[Payment], year: int | None = None
    ) -> dict[str, str]:
        monthly_payments = get_monthly_payments(payments)
        sorted_monthly_payments = dict(sorted(monthly_payments.items()))
        return {
            MONTHES[calendar.month_name[int(key)]]: (
                get_readable_price(value),
                f"/dashboard/{year}/{key}" if year else None,
            )
            for key, value in sorted_monthly_payments.items()
        }

    def get_total_monthly_payments_shares(
        self, payments: list[Payment]
    ) -> dict:
        total = self.get_total(payments)
        payments_per_categories = get_payments_sums_per_category(payments)
        payment_shares = get_payments_shares(
            payments_per_categories=payments_per_categories, total=total
        )
        return sort_payment_shares(payment_shares)

    def read(self, payment_id: int) -> Payment | None:
        statement = (
            select(Payment, Category.name)
            .join(Payment.payment_category)
            .where(Payment.id == payment_id)
        )
        results = self.session.execute(statement)
        payment = results.scalars().all()
        return (
            PaymentShowOne(
                **payment[0].__dict__, category=payment[0].payment_category.name
            )
            if payment
            else None
        )

    def create(self, payment: PaymentCreate) -> Payment:
        new_payment = Payment(**payment.model_dump())
        self.session.add(new_payment)
        self.session.commit()
        statement = select(Payment).where(Payment.id == new_payment.id)
        results = self.session.execute(statement)
        return results.scalars().one_or_none()

    def update(self, payment_id: int, to_update: PaymentUpdate):
        old_payment = self.read(payment_id)
        if old_payment.user_id != to_update.user_id:
            raise NotOwnerError(old_payment.name)
        stmt = (
            update(Payment)
            .where(Payment.id == payment_id)
            .values(
                user_id=to_update.user_id,
                name=to_update.name,
                price=to_update.price_in_kopecks,
                category_id=to_update.category_id,
                created_at=to_update.date_to_update,
                is_spending=to_update.is_spending,
            )
        )
        self.session.execute(stmt)
        self.session.commit()

    def delete(self, payment_id: int, user_id: int):
        old_payment = self.read(payment_id)
        if old_payment.user_id != user_id:
            raise NotOwnerError(old_payment.name)
        stmt = delete(Payment).where(Payment.id == payment_id)
        self.session.execute(stmt)
        self.session.commit()

    def get_all_years(self, user_id: int):
        all_payments = self.get_all_payments(user_id)
        all_payments = list({x.created_at.year for x in all_payments})
        all_payments.sort(reverse=True)
        return all_payments

    def get_dashboard(
        self,
        user_id: int,
        request: Request,
        payments: list[Payment],
        year: int = None,
        month: int | None = None,
    ):
        all_spendings = self.get_spendings(payments)
        total_spending = self.get_total_amounts(all_spendings)
        all_incomes = self.get_all_incomes(payments)
        total_income = self.get_total_amounts(all_incomes)
        available_amount = total_income - total_spending
        available_amount_frontend = get_readable_price(available_amount)
        max_date = self.get_max_date(
            user_id=user_id, limit=DateFilter(year=year, month=month)
        )
        min_date = self.get_min_date(
            user_id=user_id,
            limit=DateFilter(
                year=year,
                month=month,
            ),
        )
        total_days = self.get_total_days(max_date, min_date)
        total_per_day = self.get_total_per_day(
            total=total_spending, total_days=total_days
        )
        days_left = int(available_amount / total_per_day)
        spending = get_readable_price(total_spending)
        month = INT_TO_MONTHES.get(month)
        return {
            "request": request,
            "available_amount_frontend": available_amount_frontend,
            "days_left": days_left,
            "all_spendings": all_spendings,
            "total_per_month": self.get_monthly_payments(
                payments=all_spendings, year=year
            ),
            "total_per_day": get_readable_price(total_per_day)
            if total_per_day
            else None,
            "total_shares": list(
                self.get_total_monthly_payments_shares(all_spendings).items()
            ),
            "header_text": f"За {month} {year} года: {spending}",
        }
