from copy import deepcopy
import datetime
from sqlalchemy import func, select

from app.models import Income
from app.repositories.income import IncomeRepo
from app.schemas.income import IncomeCreate
from app.utils.tools.helpers import get_datetime_without_seconds
from tests.conftest import TEST_USER_ID


def test_create(session, client, create_income):
    create_income_copy = deepcopy(create_income)
    create_income_copy["created_at"] = datetime.datetime.now()
    create_income_copy["amount_in_rub"] = create_income_copy["amount"]
    create_income_copy.pop("amount")
    created = IncomeRepo(session).create(
        user_id=TEST_USER_ID, income=IncomeCreate(**create_income_copy)
    )
    assert created.name == create_income["name"]
    assert created.amount == create_income["amount"] * 100
    assert created.user_id == create_income["user_id"]
