import calendar
import datetime

from sqlalchemy import delete, extract, func, select, update
from sqlalchemy.orm import Session

from app.models import Category, Payment
from app.schemas.dates import DateFilter
from app.schemas.payments import (
    PaymentCreate,
    PaymentShow,
    PaymentShowOne,
    PaymentUpdate,
)
from app.utils.constants import MONTHES
from app.utils.tools.category_helpers import (
    get_payments_shares,
    get_payments_sums_per_category,
    sort_payment_shares,
)
from app.utils.tools.helpers import (
    get_monthly_payments,
    get_number_for_db,
    get_readable_price,
)


class PaymentRepo:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_all_payments(self) -> list[Payment]:
        statement = (
            select(Payment, Category.name)
            .join(Payment.payment_category)
            .order_by(Payment.created_at.desc())
        )
        res = self.session.execute(statement)
        return res.scalars().all()

    def get_payments_per_year(self, year: int) -> list[Payment]:
        statement = select(Payment).filter(
            extract("year", Payment.created_at) == year
        )
        res = self.session.execute(statement)
        return res.scalars().all()

    def get_payments_per_month(self, year: int, month: int) -> list[Payment]:
        statement = (
            select(Payment)
            .filter(extract("year", Payment.created_at) == year)
            .filter(extract("month", Payment.created_at) == month)
        )
        res = self.session.execute(statement)
        return res.scalars().all()

    def get_payments_per_year_with_category(self, year: int) -> list[Payment]:
        statement = (
            select(Payment)
            .join(Payment.payment_category)
            .filter(extract("year", Payment.created_at) == year)
        )
        res = self.session.execute(statement)
        return res.scalars().all()

    def read_all(self) -> list[Payment]:
        results = self.get_all_payments()
        return [
            PaymentShow(
                **payment.__dict__, category=payment.payment_category.name
            )
            for payment in results
        ]

    def get_total(self, payments: list[Payment]) -> int:
        total_numeric = self.sum_payments_prices(payments)
        return get_readable_price(total_numeric) if total_numeric else None

    def sum_payments_prices(self, payments):
        all_values = [x.price for x in payments]
        return sum(all_values)

    def get_max_date(self, limit: DateFilter) -> datetime.datetime:
        if not limit.year and not limit.month:
            return self.session.scalar(select(func.max(Payment.created_at)))
        if limit.year and not limit.month:
            return self.session.scalar(
                select(func.max(Payment.created_at)).filter(
                    extract("year", Payment.created_at) == limit.year
                )
            )
        if limit.year and limit.month:
            return self.session.scalar(
                select(func.max(Payment.created_at))
                .filter(extract("year", Payment.created_at) == limit.year)
                .filter(extract("month", Payment.created_at) == limit.month)
            )

    def get_min_date(self, limit: DateFilter) -> datetime.datetime:
        if not limit.year and not limit.month:
            return self.session.scalar(select(func.min(Payment.created_at)))
        if limit.year and not limit.month:
            return self.session.scalar(
                select(func.min(Payment.created_at)).filter(
                    extract("year", Payment.created_at) == limit.year
                )
            )
        if limit.year and limit.month:
            return self.session.scalar(
                select(func.min(Payment.created_at))
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
            return delta.days

    def get_total_per_day(self, total: int, total_days: int) -> str:
        try:
            return total / total_days
        except ZeroDivisionError:
            return None
        except TypeError:
            return None

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
        total = get_number_for_db(self.get_total(payments))
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

    def update(self, payment_id: int, to_upate: PaymentUpdate):
        stmt = (
            update(Payment)
            .where(Payment.id == payment_id)
            .values(
                name=to_upate.name,
                price=to_upate.price_in_kopecks,
                category_id=to_upate.category_id,
                created_at=to_upate.date_to_update,
                is_spending=to_upate.is_spending,
            )
        )
        self.session.execute(stmt)
        self.session.commit()

    def delete(self, payment_id: int):
        stmt = delete(Payment).where(Payment.id == payment_id)
        self.session.execute(stmt)
        self.session.commit()

    def get_all_years(self):
        all_payments = self.get_all_payments()
        all_payments = list({x.created_at.year for x in all_payments})
        all_payments.sort(reverse=True)
        return all_payments
