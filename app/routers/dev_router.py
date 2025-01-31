from typing import Annotated

import fastapi
from fastapi import Depends
from sqlalchemy.orm import Session

from app.models import Expense
from app.utils.dependencies import get_session
from tests.constants import EXPENSES

dev_router = fastapi.APIRouter(tags=["Dev"])


@dev_router.post("/create-expenses-in-db")
def create_expenses_in_db(session: Annotated[Session, Depends(get_session)]):
    for expense in EXPENSES:
        session.add(Expense(**expense))
        session.flush()
    session.commit()
