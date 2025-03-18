from app.repositories.expenses import ExpensesRepo
from tests.conftest import add_expenses


def test_expenses_default_sorting(client, fill_db, session, total_expenses):
    """Case: normal mode.

    Checks that the endpoint returns page
    with expenses in context.
    """
    all_expenses_before_adding = ExpensesRepo(session).read_all()
    add_expenses(session)
    session.expire_all()
    all_expenses_after_adding = ExpensesRepo(session).read_all()
    assert all_expenses_before_adding[0] != all_expenses_after_adding[0]
