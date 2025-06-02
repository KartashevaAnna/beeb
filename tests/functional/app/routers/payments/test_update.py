import datetime
from copy import copy
from unittest.mock import patch

from fastapi import status

from app.models import Payment
from app.repositories.payments import PaymentRepo
from app.settings import SETTINGS
from app.utils.tools.helpers import get_date_from_datetime
from tests.conftest import get_categories, raise_always
from tests.conftest_helpers import check_updated_payment

NAME = "potatoe"
amount = 6500


def test_template(client, payment):
    response = client.get(
        SETTINGS.urls.update_payment.format(payment_id=payment.id)
    )
    assert response.status_code == status.HTTP_200_OK
    assert payment.name in response.text
    assert str(payment.id) in response.text
    assert str(payment.amount // 100) in response.text
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


def test_name_lowercase_amount_int_is_spending_true(
    client,
    payment,
    session,
    update_payment,
):
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=update_payment,
    )

    session.expire_all()
    updated_payment = session.get(Payment, payment.id)
    check_updated_payment(updated_payment, update_payment, response)


def test_name_lowercase_amount_int_is_speding_false(
    client, payment, session, update_payment
):
    update_payment = copy(update_payment)
    update_payment["is_spending"] = False
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=update_payment,
    )
    session.expire_all()
    updated_payment = session.get(Payment, payment.id)
    check_updated_payment(updated_payment, update_payment, response)


def test_title_amount_int(client, payment, session, update_payment):
    update_payment = copy(update_payment)
    update_payment["name"] = NAME.title()
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=update_payment,
    )
    session.expire_all()
    updated_payment = session.get(Payment, payment.id)
    check_updated_payment(updated_payment, update_payment, response)


def test_name_upper_amount_int(client, payment, session, update_payment):
    update_payment = copy(update_payment)
    update_payment["name"] = NAME.upper()
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=update_payment,
    )
    session.expire_all()
    updated_payment = session.get(Payment, payment.id)
    check_updated_payment(updated_payment, update_payment, response)


def test_name_lowercase_amount_frontend(
    client, payment, session, update_payment
):
    update_payment = copy(update_payment)
    update_payment["amount"] = "65₽"
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=update_payment,
    )
    session.expire_all()
    updated_payment = session.get(Payment, payment.id)
    check_updated_payment(updated_payment, update_payment, response)


def test_name_lowercase_amount_int_zero(client, payment, update_payment):
    update_payment = copy(update_payment)
    update_payment["amount"] = 0
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=update_payment,
    )
    assert "number must be positive" in response.text


def test_name_lowercase_amount_frontend_zero(client, payment, update_payment):
    update_payment = copy(update_payment)
    update_payment["amount"] = "00₽"
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=update_payment,
    )
    assert "number must be positive" in response.text


def test_name_lowercase_amount_frontend_negative(
    client, payment, update_payment
):
    update_payment = copy(update_payment)
    update_payment["amount"] = "-56₽"
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=update_payment,
    )
    assert "number must be positive" in response.text


def test_name_lowercase_amount_int_negative(client, payment, update_payment):
    update_payment = copy(update_payment)
    update_payment["amount"] = "-56₽"
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=update_payment,
    )
    assert "number must be positive" in response.text


def test_404(client):
    response = client.get(SETTINGS.urls.update_payment.format(payment_id=1))
    assert response.status_code == 404


@patch.object(PaymentRepo, "update", raise_always)
def test_update_payment_any_other_exception(client, payment, update_payment):
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=update_payment,
    )
    assert response.status_code == 501


def test_update_category(client, session, fill_db, payment, update_payment):
    previous_category = payment.payment_category.name
    categories = get_categories(session)
    categories_names = [x.name for x in categories]
    categories = {x.name: x.id for x in categories}
    categories_names.remove(previous_category)
    new_category_name = categories_names[0]
    update_payment = copy(update_payment)
    update_payment["category"] = new_category_name
    update_payment.pop("created_at", None)
    update_payment.pop("categoty_id", None)

    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=update_payment,
    )
    session.expire_all()
    updated_payment = session.get(Payment, payment.id)
    update_payment["category_id"] = categories[new_category_name]

    check_updated_payment(
        updated_payment=updated_payment,
        payment_update=update_payment,
        response=response,
    )
    assert updated_payment.payment_category.name != previous_category


def test_update_date(client, session, payment, update_payment):
    previous_date = payment.created_at
    new_date = payment.created_at - datetime.timedelta(weeks=-4)
    new_date = new_date.astimezone()
    update_payment["date"] = get_date_from_datetime(new_date)
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=update_payment,
    )
    session.expire_all()
    updated_payment = session.get(Payment, payment.id)
    check_updated_payment(updated_payment, update_payment, response)
    assert updated_payment.created_at != previous_date
    assert updated_payment.created_at.date() == new_date.date()


def test_no_cookie(client, payment, update_payment):
    client.cookies = {}
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=update_payment,
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_stale_token_post(client, payment, update_payment, stale_token):
    client.cookies = {"token": stale_token}
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=update_payment,
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_wrong_token_post(
    client, payment, update_payment, wrong_token, session
):
    client.cookies = {"token": wrong_token}
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=update_payment,
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers.get("location") == SETTINGS.urls.login


def test_wrong_user(client, payment, session, update_payment, wrong_user_token):
    client.cookies["token"] = wrong_user_token
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=update_payment,
    )
    assert response.status_code == status.HTTP_501_NOT_IMPLEMENTED
    assert response.template.name == SETTINGS.templates.read_payment
    session.expire_all()
    not_updated_payment = session.get(Payment, payment.id)
    assert payment == not_updated_payment
