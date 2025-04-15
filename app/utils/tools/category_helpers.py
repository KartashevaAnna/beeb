import math

from app.models import Category, Payment
from app.schemas.categories import CategoryCreate


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
                payment.price
            )
        else:
            payments_sums_per_category[payment.payment_category.name] = (
                payment.price
                + payments_sums_per_category[payment.payment_category.name]
            )
    return payments_sums_per_category


def get_payments_shares(payments_per_categories: dict, total: int) -> dict:
    return {
        key: math.floor(payments_per_categories[key] * 100 / total)
        for key in payments_per_categories
    }


def add_category_to_db(session, name: str) -> Category:
    category = Category(**CategoryCreate(name=name).__dict__)
    session.add(category)
    session.commit()
    return category
