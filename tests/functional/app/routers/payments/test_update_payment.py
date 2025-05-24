import datetime
from copy import copy
from unittest.mock import patch

from fastapi import status

from app.models import Payment
from app.repositories.payments import PaymentRepo
from app.settings import SETTINGS
from app.utils.tools.helpers import get_date_from_datetime
from tests.conftest import clean_db, get_categories, raise_always
from tests.conftest_helpers import check_updated_payment

NAME = "potatoe"
PRICE = 6500


def test_template(client, payment):
    response = client.get(
        SETTINGS.urls.update_payment.format(payment_id=payment.id)
    )
    assert response.status_code == status.HTTP_200_OK
    assert payment.name in response.text
    assert str(payment.id) in response.text
    assert str(payment.price // 100) in response.text
    assert payment.payment_category.name in response.text


def test_template_no_cookie(client, payment):
    client.cookies = {}
    response = client.get(
        SETTINGS.urls.update_payment.format(payment_id=payment.id)
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_template_stale_token(client, payment, stale_token):
    client.cookies = {"token": stale_token}
    response = client.get(
        SETTINGS.urls.update_payment.format(payment_id=payment.id)
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_template_wrong_token(client, payment, wrong_token):
    client.cookies = {"token": wrong_token}
    response = client.get(
        SETTINGS.urls.update_payment.format(payment_id=payment.id)
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_name_lowercase_price_int_is_spending_true(
    client,
    payment,
    session,
    payment_update,
):
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=payment_update,
    )

    session.expire_all()
    updated_payment = session.get(Payment, payment.id)
    check_updated_payment(updated_payment, payment_update, response)


def test_name_lowercase_price_int_is_speding_false(
    client, payment, session, payment_update
):
    payment_update = copy(payment_update)
    payment_update["is_spending"] = False
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=payment_update,
    )
    session.expire_all()
    updated_payment = session.get(Payment, payment.id)
    check_updated_payment(updated_payment, payment_update, response)


def test_title_price_int(client, payment, session, payment_update):
    payment_update = copy(payment_update)
    payment_update["name"] = NAME.title()
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=payment_update,
    )
    session.expire_all()
    updated_payment = session.get(Payment, payment.id)
    check_updated_payment(updated_payment, payment_update, response)


def test_name_upper_price_int(client, payment, session, payment_update):
    payment_update = copy(payment_update)
    payment_update["name"] = NAME.upper()
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=payment_update,
    )
    session.expire_all()
    updated_payment = session.get(Payment, payment.id)
    check_updated_payment(updated_payment, payment_update, response)


def test_name_lowercase_price_frontend(
    client, payment, session, payment_update
):
    payment_update = copy(payment_update)
    payment_update["price"] = "65₽"
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=payment_update,
    )
    session.expire_all()
    updated_payment = session.get(Payment, payment.id)
    check_updated_payment(updated_payment, payment_update, response)


def test_name_lowercase_price_int_zero(client, payment, payment_update):
    payment_update = copy(payment_update)
    payment_update["price"] = 0
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=payment_update,
    )
    assert "number must be positive" in response.text


def test_name_lowercase_price_frontend_zero(client, payment, payment_update):
    payment_update = copy(payment_update)
    payment_update["price"] = "00₽"
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=payment_update,
    )
    assert "number must be positive" in response.text


def test_name_lowercase_price_frontend_negative(
    client, payment, payment_update
):
    payment_update = copy(payment_update)
    payment_update["price"] = "-56₽"
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=payment_update,
    )
    assert "number must be positive" in response.text


def test_name_lowercase_price_int_negative(client, payment, payment_update):
    payment_update = copy(payment_update)
    payment_update["price"] = "-56₽"
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=payment_update,
    )
    assert "number must be positive" in response.text


def test_404(client):
    response = client.get(SETTINGS.urls.update_payment.format(payment_id=1))
    assert response.status_code == 404


@patch.object(PaymentRepo, "update", raise_always)
def test_update_payment_any_other_exception(client, payment, payment_update):
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=payment_update,
    )
    assert response.status_code == 501


def test_update_category(client, session, fill_db, payment, payment_update):
    previous_category = payment.payment_category.name
    categories = get_categories(session)
    categories_names = [x.name for x in categories]
    categories = {x.name: x.id for x in categories}
    categories_names.remove(previous_category)
    new_category_name = categories_names[0]
    payment_update = copy(payment_update)
    payment_update["category"] = new_category_name
    payment_update.pop("created_at", None)
    payment_update.pop("categoty_id", None)

    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=payment_update,
    )
    session.expire_all()
    updated_payment = session.get(Payment, payment.id)
    payment_update["category_id"] = categories[new_category_name]

    check_updated_payment(
        updated_payment=updated_payment,
        payment_update=payment_update,
        response=response,
    )
    assert updated_payment.payment_category.name != previous_category


def test_update_date(client, session, payment, payment_update):
    previous_date = payment.created_at
    new_date = payment.created_at - datetime.timedelta(weeks=-4)
    new_date = new_date.astimezone()
    payment_update["date"] = get_date_from_datetime(new_date)
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=payment_update,
    )
    session.expire_all()
    updated_payment = session.get(Payment, payment.id)
    check_updated_payment(updated_payment, payment_update, response)
    assert updated_payment.created_at != previous_date
    assert updated_payment.created_at.date() == new_date.date()


def test_no_cookie(client, payment, payment_update):
    client.cookies = {}
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=payment_update,
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_stale_token_post(client, payment, payment_update, stale_token):
    client.cookies = {"token": stale_token}
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=payment_update,
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_wrong_token_post(
    client, payment, payment_update, wrong_token, session
):
    client.cookies = {"token": wrong_token}
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=payment_update,
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login
    clean_db(session)


def test_wrong_user(client, payment, session, payment_update, wrong_user_token):
    client.cookies["token"] = wrong_user_token
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=payment_update,
    )
    assert response.status_code == status.HTTP_501_NOT_IMPLEMENTED
    assert response.template.name == SETTINGS.templates.read_payment
    session.expire_all()
    not_updated_payment = session.get(Payment, payment.id)
    assert payment == not_updated_payment
