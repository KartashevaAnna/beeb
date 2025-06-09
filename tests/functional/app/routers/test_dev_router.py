from app.utils.constants import PRODUCTS
from tests.conftest import clean_db, get_categories, get_payments


def test_dev_router_populating_the_database_with_payments(client, session):
    #  check that there are no payments in the database
    all_payments = get_payments(session)
    assert not all_payments
    response = client.post("/populate-payments", data={"user_id": 1})
    assert response.status_code == 200
    # verify that payments appered in the database
    all_payments = get_payments(session)
    assert all_payments
    assert len(all_payments) == len(PRODUCTS)


def test_dev_router_populating_the_database_with_categories(client, session):
    #  check that there are no categories in the database
    all_categories = get_categories(session)
    assert not all_categories
    response = client.post("/populate-categories", data={"user_id": 1})
    assert response.status_code == 200
    # verify that categories appered in the database
    all_categories = get_categories(session)
    assert all_categories
