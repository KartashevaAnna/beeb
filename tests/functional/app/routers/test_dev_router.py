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
    clean_db(session)


def test_dev_router_populating_the_database_with_categories(client, session):
    #  check that there are no categories in the database
    all_categories = get_categories(session)
    assert not all_categories
    response = client.post("/populate-categories", data={"user_id": 1})
    assert response.status_code == 200
    # verify that categories appered in the database
    all_categories = get_categories(session)
    assert all_categories


def test_upload_payments_from_ods_file_non_clean_db(client, session, fill_db):
    all_categories_before = get_categories(session)
    all_payments_before = get_payments(session)
    response = client.post("/upload-payments", data={"user_id": 1})
    assert response.status_code == 200
    session.expire_all()
    all_categories_after = get_categories(session)
    all_payments_after = get_payments(session)
    assert len(all_categories_after) > len(all_categories_before)
    assert len(all_payments_after) > len(all_payments_before)


def test_upload_payments_from_ods_file_clean_db(client, session, fill_db):
    all_categories_before = get_categories(session)
    all_payments_before = get_payments(session)
    response = client.post("/upload-payments")
    assert response.status_code == 200
    session.expire_all()
    all_categories_after = get_categories(session)
    all_payments_after = get_payments(session)
    assert len(all_categories_after) > len(all_categories_before)
    assert len(all_payments_after) > len(all_payments_before)
