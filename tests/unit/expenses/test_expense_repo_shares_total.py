from app.repositories.expenses import ExpensesRepo


def test_get_monthly_expenses_shares_total(client, fill_db, session):
    """Case: normal mode. Verify monthly expenses.

    Checks that the helper function called by the repo
    correctly calculates the share of expenses per category in overall expenses.
    """
    monthly_expenses_shares_total = ExpensesRepo(
        session
    ).get_total_monthly_expenses_shares()
    checksum = int(sum(list(monthly_expenses_shares_total.values())))
    assert checksum == 100
