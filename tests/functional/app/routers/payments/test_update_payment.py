import datetime
from copy import copy
from unittest.mock import patch

from app.models import Payment
from app.repositories.payments import PaymentRepo
from app.settings import SETTINGS
from app.utils.tools.helpers import get_date_from_datetime
from tests.conftest import get_categories, raise_always
from tests.conftest_helpers import check_updated_payment

NAME = "potatoe"
PRICE = 6500


def test_serve_template_update_payment(client, payment):
    """Case: endpoint returns form to update an payment."""
    response = client.get(
        SETTINGS.urls.update_payment.format(payment_id=payment.id)
    )
    assert response.status_code == 200
    assert payment.name in response.text
    assert str(payment.id) in response.text
    assert str(payment.price // 100) in response.text
    assert payment.payment_category.name in response.text


def test_update_payment_standard_mode_name_lowercase_price_int_is_spending_true(
    client, payment, session, payment_update
):
    """Case: endpoint updates an payment.

    Name is lowercase, price is integer.
    """

    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=payment_update,
    )
    session.expire_all()
    updated_payment = session.get(Payment, payment.id)
    check_updated_payment(updated_payment, payment_update, response)


def test_update_payment_standard_mode_name_lowercase_price_int_is_speding_false(
    client, payment, session, payment_update
):
    """Case: endpoint updates an payment.

    Name is lowercase, price is integer.
    """
    payment_update = copy(payment_update)
    payment_update["is_spending"] = False
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=payment_update,
    )
    session.expire_all()
    updated_payment = session.get(Payment, payment.id)
    check_updated_payment(updated_payment, payment_update, response)


def test_update_payment_standard_mode_name_title_price_int(
    client, payment, session, payment_update
):
    """Case: endpoint updates an payment.

    Name is a title, price is integer.
    """
    payment_update = copy(payment_update)
    payment_update["name"] = NAME.title()
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=payment_update,
    )
    session.expire_all()
    updated_payment = session.get(Payment, payment.id)
    check_updated_payment(updated_payment, payment_update, response)


def test_update_payment_standard_mode_name_upper_price_int(
    client, payment, session, payment_update
):
    """Case: endpoint updates an payment.

    Name is uppercase, price is integer.
    """
    payment_update = copy(payment_update)
    payment_update["name"] = NAME.upper()
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=payment_update,
    )
    session.expire_all()
    updated_payment = session.get(Payment, payment.id)
    check_updated_payment(updated_payment, payment_update, response)


def test_update_payment_standard_mode_name_lowercase_price_frontend(
    client, payment, session, payment_update
):
    """Case: endpoint updates an payment.

    Name is lowercase, price is localized string with currency symbol.
    """
    payment_update = copy(payment_update)
    payment_update["price"] = "65₽"
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=payment_update,
    )
    session.expire_all()
    updated_payment = session.get(Payment, payment.id)
    check_updated_payment(updated_payment, payment_update, response)


def test_update_payment_name_lowercase_price_int_zero(
    client, payment, payment_update
):
    """Case: endpoint fails updating an payment.

    Name is lowercase, price is zero (int).
    """
    payment_update = copy(payment_update)
    payment_update["price"] = 0
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=payment_update,
    )
    assert "number must be positive" in response.text


def test_update_payment_name_lowercase_price_frontend_zero(
    client, payment, payment_update
):
    """Case: endpoint fails updating an payment.

    Name is lowercase, price is zero (localized string with currency symbol).
    """
    payment_update = copy(payment_update)
    payment_update["price"] = "00₽"
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=payment_update,
    )
    assert "number must be positive" in response.text


def test_update_payment_name_lowercase_price_frontend_negative(
    client, payment, payment_update
):
    """Case: endpoint fails updating an payment.

    Name is lowercase, price is negative
    (localized string with currency symbol).
    """
    payment_update = copy(payment_update)
    payment_update["price"] = "-56₽"
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=payment_update,
    )
    assert "number must be positive" in response.text


def test_update_payment_name_lowercase_price_int_negative(
    client, payment, payment_update
):
    """Case: endpoint fails updating an payment.

    Name is lowercase, price is a negative integer.
    """
    payment_update = copy(payment_update)
    payment_update["price"] = "-56₽"
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=payment_update,
    )
    assert "number must be positive" in response.text


def test_update_payment_serve_template_404(client):
    """Case: user requests update of a nonexistant payment.

    Checks that the endpoint returns a 404 status code.
    """
    response = client.get(SETTINGS.urls.update_payment.format(payment_id=1))
    assert response.status_code == 404


@patch.object(PaymentRepo, "update", raise_always)
def test_update_payment_exception(client, payment, payment_update):
    """Case: any exception is thrown."""
    response = client.post(
        SETTINGS.urls.update_payment.format(payment_id=payment.id),
        data=payment_update,
    )
    assert response.status_code == 501


def test_update_payment_update_category(
    client, session, fill_db, payment, payment_update
):
    """Case: endpoint updates an payment with a new category.

    Name is uppercase, price is integer.
    """
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


def test_update_payment_update_date(client, session, payment, payment_update):
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
