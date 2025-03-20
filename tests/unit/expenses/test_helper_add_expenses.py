from sqlalchemy import delete, select

from app.models import Expense
from app.utils.tools.helpers import add_expenses_to_db


def test_add_expenses_to_db(session):
    """Check that the helper populates the database with expenses."""
    # check that there are no expenses in the database
    statement = select(Expense)
    res = session.execute(statement)
    all_expenses = res.scalars().all()
    assert not all_expenses
    # get a response from the helper function adding expenses to the database
    add_expenses_to_db(session)
    session.expire_all()
    # verify that expenses appered in the database
    statement = select(Expense)
    res = session.execute(statement)
    all_expenses = res.scalars().all()
    assert all_expenses
    assert len(all_expenses) == 1
    #  delete the created expense so that it does not convolute further tests
    stmt = delete(Expense).where(Expense.id > 0)
    session.execute(stmt)
    session.commit()
    # check that there are no expenses left in the database
    statement = select(Expense)
    res = session.execute(statement)
    all_expenses = res.scalars().all()
    assert not all_expenses
