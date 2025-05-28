import math

from app.models import Category, Payment
from app.schemas.categories import CategoryCreate
from app.utils.tools.helpers import get_readable_amount


def get_payments_sums_per_category(
    all_payments: list[Payment],
) -> dict[int, str]:
    payments_sums_per_category = {}
    for payment in all_payments:
        if (
            payment.payment_category.name
            not in payments_sums_per_category.keys()
        ):
            payments_sums_per_category[payment.payment_category.name] = (
                payment.amount
            )
        else:
            payments_sums_per_category[payment.payment_category.name] = (
                payment.amount
                + payments_sums_per_category[payment.payment_category.name]
            )
    return payments_sums_per_category


def get_payments_shares(payments_per_categories: dict, total: int) -> dict:
    return {
        math.floor(payments_per_categories[key] * 100 / total): (
            key,
            get_readable_amount(payments_per_categories[key]),
        )
        for key in payments_per_categories
    }


def sort_payment_shares(payments_per_categories: dict) -> dict:
    return dict(
        sorted(
            payments_per_categories.items(),
            key=lambda item: item[0],
            reverse=True,
        )
    )


def add_category_to_db(session, name: str, user_id: int) -> Category:
    category = Category(**CategoryCreate(name=name, user_id=user_id).__dict__)
    session.add(category)
    session.commit()
    return category
