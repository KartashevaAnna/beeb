from app.utils.tools.helpers import add_expenses_to_db
from tests.conftest import get_expenses


def test_add_expenses_to_db(session, category):
    """Check that the helper populates the database with expenses."""
    # check that there are no expenses in the database
    all_expenses = get_expenses(session)
    assert not all_expenses
    # get a response from the helper function adding expenses to the database
    add_expenses_to_db(session, category_id=category.id)
    session.expire_all()
    # verify that expenses appered in the database
    all_expenses = get_expenses(session)
    assert all_expenses
    assert len(all_expenses) == 1
