import calendar
from typing import List

from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session
from sqlalchemy.sql import functions

from app.models import Category, Payment
from app.schemas.payments import (
    PaymentCreate,
    Paymentshow,
    PaymentshowOne,
    PaymentUpdate,
)
from app.utils.constants import MONTHES
from app.utils.tools.helpers import (
    get_monthly_payments,
    get_number_for_db,
    get_payments_shares,
    get_payments_sums_per_category,
    get_readable_price,
)


class PaymentRepo:
    def __init__(self, session: Session) -> None:
        self.session = session

    def read_all(self) -> List[Payment]:
        statement = (
            select(Payment, Category.name)
            .join(Payment.payment_category)
            .order_by(Payment.created_at.desc())
        )
        res = self.session.execute(statement)
        results = res.scalars().all()
        return [
            Paymentshow(
                **payment.__dict__, category=payment.payment_category.name
            )
            for payment in results
        ]

    def get_total(self) -> int:
        statement = select(functions.sum(Payment.price))
        results = self.session.execute(statement)
        total_numeric = results.scalars().first()
        return get_readable_price(total_numeric) if total_numeric else None

    def get_total_days(self) -> int:
        max_date = self.session.scalar(select(func.max(Payment.created_at)))
        min_date = self.session.scalar(select(func.min(Payment.created_at)))
        if not any([max_date, min_date]):
            return 0
        else:
            delta = max_date - min_date
            return delta.days

    def get_total_per_day_overall(self) -> str:
        try:
            return get_readable_price(
                get_number_for_db(self.get_total()) / self.get_total_days()
            )
        except ZeroDivisionError:
            return None

    def get_total_per_month(self) -> dict[str, str]:
        stmt = select(Payment)
        results = self.session.execute(stmt)
        all_payments = results.scalars().all()
        monthly_payments = get_monthly_payments(all_payments)
        sorted_monthly_payments = dict(sorted(monthly_payments.items()))
        return {
            MONTHES[calendar.month_name[int(key)]]: get_readable_price(value)
            for key, value in sorted_monthly_payments.items()
        }

    def get_total_monthly_payments_shares(self) -> dict:
        stmt = select(Payment).join(Payment.payment_category)
        results = self.session.execute(stmt)
        all_payments = results.scalars().all()
        total = get_number_for_db(self.get_total())
        payments_per_categories = get_payments_sums_per_category(all_payments)
        return get_payments_shares(
            payments_per_categories=payments_per_categories, total=total
        )

    def read(self, payment_id: int) -> Payment | None:
        statement = (
            select(Payment, Category.name)
            .join(Payment.payment_category)
            .where(Payment.id == payment_id)
        )
        results = self.session.execute(statement)
        payment = results.scalars().all()
        return (
            PaymentshowOne(
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
            )
        )
        self.session.execute(stmt)
        self.session.commit()

    def delete(self, payment_id: int):
        stmt = delete(Payment).where(Payment.id == payment_id)
        self.session.execute(stmt)
        self.session.commit()
