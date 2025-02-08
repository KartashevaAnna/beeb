from typing import Annotated

import fastapi
from fastapi import Depends
from sqlalchemy.orm import Session

from app.utils.dependencies import get_session
from app.utils.tools.helpers import add_expenses_to_db
from tests.constants import PRODUCTS

dev_router = fastapi.APIRouter(tags=["Dev"])


@dev_router.post("/create-expenses-in-db")
def create_expenses_in_db(session: Annotated[Session, Depends(get_session)]):
    for _ in range(len(PRODUCTS)):
        add_expenses_to_db(session)
