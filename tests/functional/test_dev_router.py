from app.utils.constants import PRODUCTS
from tests.conftest import clean_db, get_categories, get_expenses


def test_dev_router_populating_the_database_with_expenses(client, session):
    #  check that there are no expenses in the database
    all_expenses = get_expenses(session)
    assert not all_expenses
    response = client.post("/populate-expenses")
    assert response.status_code == 200
    # verify that expenses appered in the database
    all_expenses = get_expenses(session)
    assert all_expenses
    assert len(all_expenses) == len(PRODUCTS)
    clean_db(session)


def test_dev_router_populating_the_database_with_categories(client, session):
    #  check that there are no categories in the database
    all_categories = get_categories(session)
    assert not all_categories
    response = client.post("/populate-categories")
    assert response.status_code == 200
    # verify that categories appered in the database
    all_categories = get_categories(session)
    assert all_categories
