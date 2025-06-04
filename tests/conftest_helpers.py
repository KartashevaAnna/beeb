from copy import deepcopy

from fastapi import Response, status

from app.models import Income, Payment
from app.settings import SETTINGS
from app.utils.tools.helpers import convert_to_copecks, get_number_for_db


def remove_id(to_change: dict) -> dict:
    new_dict = deepcopy(to_change)
    new_dict.pop("id", None)
    return new_dict


def change_to_a_defined_category(payment_as_dict, category) -> dict:
    new_dict = dict(payment_as_dict)
    new_dict["category_id"] = category.id
    return new_dict


def check_created_payment(
    create_payment: dict, payment: Payment, response: Response
):
    assert response.status_code == 303
    if create_payment.get("grams"):
        assert (
            response.headers.get("location")
            == SETTINGS.urls.create_payment_food
        )
    else:
        assert (
            response.headers.get("location")
            == SETTINGS.urls.create_payment_non_food
        )
    assert payment.name == create_payment["name"]
    assert payment.amount == convert_to_copecks(create_payment["amount"])
    assert payment.category_id == create_payment["category_id"]


def check_created_income(
    create_income: dict, income: Income, response: Response
):
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.payments
    assert income.name == create_income["name"]
    assert income.amount == convert_to_copecks(create_income["amount"])


def check_updated_payment(
    updated_payment: Payment, payment_update: dict, response: Response
):
    payment_update = deepcopy(payment_update)
    payment_update["name"] = payment_update["name"].lower()
    assert response.status_code == 303
    assert response.headers.get("location") == SETTINGS.urls.payments
    assert updated_payment.id == payment_update["id"]
    assert updated_payment.name == payment_update["name"]
    if isinstance(payment_update["amount"], str):
        payment_update["amount"] = get_number_for_db(payment_update["amount"])
        # get_number_for_db calls convert_to_copecks inside it
    else:
        payment_update["amount"] = convert_to_copecks(payment_update["amount"])
    assert updated_payment.amount == payment_update["amount"]
    assert updated_payment.payment_category.id == payment_update["category_id"]
    assert updated_payment.user_id == payment_update["user_id"]


def check_updated_income(
    updated_income: Income, income_update: dict, response: Response
):
    income_update = deepcopy(income_update)
    assert response.status_code == 303
    assert response.headers.get("location") == SETTINGS.urls.payments
    assert updated_income.name == income_update["frontend_name"]
    assert updated_income.amount == income_update["amount_in_rub"] * 100
