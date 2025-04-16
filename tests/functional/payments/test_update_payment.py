import datetime
from unittest.mock import patch

from app.models import Payment
from app.repositories.payments import PaymentRepo
from app.settings import SETTINGS
from app.utils.tools.helpers import (
    convert_to_copecks,
    get_date_from_datetime,
    get_readable_price,
)
from tests.conftest import get_categories, raise_always

NAME = "potatoe"
PRICE = 6500


def test_serve_template_update_payment(client, payment):
    """Case: endpoint returns form to update an payment."""
    response = client.get(
        SETTINGS.urls.update_payment.format(payment_id=payment.id)
    )
    assert response.status_code == 200
    assert payment.name.title() in response.text
    assert str(payment.id) in response.text
    assert get_readable_price(payment.price) in response.text
    assert payment.payment_category.name in response.text


def test_update_payment_standard_mode_name_lowercase_price_int(
    client, payment, session
):
    """Case: endpoint updates an payment.

    Name is lowercase, price is integer.
    """

    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data={
            "name": NAME,
            "price": PRICE,
            "payment_id": payment.id,
            "category": payment.payment_category.name,
            "form_disabled": True,
            "date": get_date_from_datetime(payment.created_at),
        },
    )
    assert response.status_code == 303
    assert response.headers.get("location") == SETTINGS.urls.payments
    session.expire_all()
    updated_payment = session.get(Payment, payment.id)
    assert payment.id == updated_payment.id
    assert updated_payment.name == NAME
    assert updated_payment.price == convert_to_copecks(PRICE)
    assert updated_payment.payment_category == payment.payment_category


def test_update_payment_standard_mode_name_title_price_int(
    client, payment, session
):
    """Case: endpoint updates an payment.

    Name is a title, price is integer.
    """
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data={
            "name": NAME.title(),
            "price": PRICE,
            "category": payment.payment_category.name,
            "form_disabled": True,
            "date": get_date_from_datetime(payment.created_at),
        },
    )
    assert response.status_code == 303
    assert response.headers.get("location") == SETTINGS.urls.payments
    session.expire_all()
    updated_payment = session.get(Payment, payment.id)
    assert payment.id == updated_payment.id
    assert updated_payment.name == NAME


def test_update_payment_standard_mode_name_upper_price_int(
    client, payment, session
):
    """Case: endpoint updates an payment.

    Name is uppercase, price is integer.
    """
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data={
            "name": NAME.upper(),
            "price": PRICE,
            "category": payment.payment_category.name,
            "form_disabled": True,
            "date": get_date_from_datetime(payment.created_at),
        },
    )
    assert response.status_code == 303
    assert response.headers.get("location") == SETTINGS.urls.payments
    session.expire_all()
    updated_payment = session.get(Payment, payment.id)
    assert payment.id == updated_payment.id
    assert updated_payment.name == NAME
    assert (
        updated_payment.payment_category.name == payment.payment_category.name
    )


def test_update_payment_standard_mode_name_lowercase_price_frontend(
    client, payment, session
):
    """Case: endpoint updates an payment.

    Name is lowercase, price is localized string with currency symbol.
    """
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data={
            "name": NAME,
            "price": "65₽",
            "category": payment.payment_category.name,
            "form_disabled": True,
            "date": get_date_from_datetime(payment.created_at),
        },
    )
    assert response.status_code == 303
    assert response.headers.get("location") == SETTINGS.urls.payments
    session.expire_all()
    updated_payment = session.get(Payment, payment.id)
    assert payment.id == updated_payment.id
    assert updated_payment.name == NAME
    assert updated_payment.price == PRICE
    assert (
        updated_payment.payment_category.name == payment.payment_category.name
    )


def test_update_payment_name_lowercase_price_int_zero(client, payment):
    """Case: endpoint fails updating an payment.

    Name is lowercase, price is zero (int).
    """
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data={
            "name": NAME,
            "price": 0,
            "category": payment.payment_category.name,
            "form_disabled": True,
            "date": get_date_from_datetime(payment.created_at),
        },
    )
    assert "number must be positive" in response.text


def test_update_payment_name_lowercase_price_frontend_zero(
    client,
    payment,
):
    """Case: endpoint fails updating an payment.

    Name is lowercase, price is zero (localized string with currency symbol).
    """
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data={
            "name": NAME,
            "price": "00₽",
            "category": payment.payment_category.name,
            "form_disabled": True,
            "date": get_date_from_datetime(payment.created_at),
        },
    )
    assert "number must be positive" in response.text


def test_update_payment_name_lowercase_price_frontend_negative(
    client,
    payment,
):
    """Case: endpoint fails updating an payment.

    Name is lowercase, price is negative
    (localized string with currency symbol).
    """
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data={
            "name": NAME,
            "price": "-56₽",
            "category": payment.payment_category.name,
            "form_disabled": True,
            "date": get_date_from_datetime(payment.created_at),
        },
    )
    assert "number must be positive" in response.text


def test_update_payment_name_lowercase_price_int_negative(client, payment):
    """Case: endpoint fails updating an payment.

    Name is lowercase, price is a negative integer.
    """
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data={
            "name": NAME,
            "price": -56,
            "category": payment.payment_category.name,
            "form_disabled": True,
            "date": get_date_from_datetime(payment.created_at),
        },
    )
    assert "number must be positive" in response.text


def test_update_payment_serve_template_404(client):
    """Case: user requests update of a nonexistant payment.

    Checks that the endpoint returns a 404 status code.
    """
    response = client.get(SETTINGS.urls.update_payment.format(payment_id=1))
    assert response.status_code == 404


@patch.object(PaymentRepo, "update", raise_always)
def test_update_payment_exception(client, payment):
    """Case: any exception is thrown."""
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data={
            "name": NAME,
            "price": 56,
            "category": payment.payment_category.name,
            "form_disabled": True,
            "date": get_date_from_datetime(payment.created_at),
        },
    )
    assert response.status_code == 501
    assert "exception" in response.text


def test_update_payment_update_category(client, session, fill_db, payment):
    """Case: endpoint updates an payment with a new category.

    Name is uppercase, price is integer.
    """
    previous_category = payment.payment_category.name
    categories = get_categories(session)
    categories = [x.name for x in categories]
    categories.remove(previous_category)
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data={
            "name": NAME,
            "price": PRICE,
            "category": categories[0],
            "form_disabled": True,
            "date": get_date_from_datetime(payment.created_at),
        },
    )
    assert response.status_code == 303
    assert response.headers.get("location") == SETTINGS.urls.payments
    session.expire_all()
    updated_payment = session.get(Payment, payment.id)
    assert payment.id == updated_payment.id
    assert updated_payment.name == NAME
    assert updated_payment.price == convert_to_copecks(PRICE)
    assert updated_payment.payment_category.name != previous_category


def test_update_payment_update_date(client, session, payment):
    previous_date = payment.created_at
    new_date = payment.created_at - datetime.timedelta(weeks=-4)
    new_date = new_date.astimezone()
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data={
            "name": NAME.upper(),
            "price": PRICE,
            "category": payment.payment_category.name,
            "form_disabled": True,
            "date": get_date_from_datetime(new_date),
        },
    )
    assert response.status_code == 303
    assert response.headers.get("location") == SETTINGS.urls.payments
    session.expire_all()
    updated_payment = session.get(Payment, payment.id)
    assert payment.id == updated_payment.id
    assert updated_payment.created_at != previous_date
    assert updated_payment.created_at.date() == new_date.date()
