from sqlalchemy import delete, select

from app.models import Expense
from app.utils.constants import PRODUCTS


def test_dev_router_populating_the_database(client, session):
    #  check that there are no expenses in the database
    statement = select(Expense)
    res = session.execute(statement)
    all_expenses = res.scalars().all()
    assert not all_expenses
    response = client.post("/create-expenses-in-db")
    assert response.status_code == 200
    # verify that expenses appered in the database
    statement = select(Expense)
    res = session.execute(statement)
    all_expenses = res.scalars().all()
    assert all_expenses
    assert len(all_expenses) == len(PRODUCTS)
    #  delete the created expense so that it does not convolute further tests
    stmt = delete(Expense).where(Expense.id > 0)
    session.execute(stmt)
    session.commit()
    # check that there are no expenses left in the database
    statement = select(Expense).order_by(Expense.created_at.desc())
    res = session.execute(statement)
    all_expenses = res.scalars().all()
    assert not all_expenses
