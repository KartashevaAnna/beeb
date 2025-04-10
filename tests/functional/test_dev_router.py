from sqlalchemy import delete, select

from app.models import Category, Expense
from app.utils.constants import PRODUCTS
from tests.conftest import get_categories, get_expenses


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
    #  delete the created expense so that it does not convolute further tests
    stmt = delete(Expense).where(Expense.id > 0)
    session.execute(stmt)
    stmt = delete(Category).where(Category.id > 0)
    session.execute(stmt)
    session.commit()
    # check that there are no expenses left in the database
    statement = select(Expense).order_by(Expense.created_at.desc())
    res = session.execute(statement)
    all_expenses = res.scalars().all()
    assert not all_expenses


def test_dev_router_populating_the_database_with_categories(client, session):
    #  check that there are no categories in the database
    all_categories = get_categories(session)
    assert not all_categories
    response = client.post("/populate-categories")
    assert response.status_code == 200
    # verify that categories appered in the database
    all_categories = get_categories(session)
    assert all_categories
