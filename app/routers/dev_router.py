from copy import deepcopy
import csv
import datetime
import locale
import os
import random
import select
from typing import Annotated
from fastapi import APIRouter

from fastapi import Depends
from pyexcel_odsr import get_data
from sqlalchemy.orm import Session

from app.models import Category, Payment
from app.repositories.categories import CategoryRepo
from app.repositories.payments import PaymentRepo
from app.schemas.categories import CategoryCreate
from app.settings import PAYMENTS_TO_UPLOAD_DIR
from app.utils.constants import CATEGORIES, PRODUCTS
from app.utils.dependencies import categories_repo, get_session, payments_repo
from app.utils.tools.category_helpers import add_category_to_db
from app.utils.tools.helpers import (
    add_payments_to_db,
    convert_to_copecks,
    get_date_for_database,
    get_number_for_db,
)

dev_router = APIRouter(tags=["Dev"], include_in_schema=True)


@dev_router.post("/populate-categories")
def create_category_in_db(
    session: Annotated[Session, Depends(get_session)],
    repo: Annotated[CategoryRepo, Depends(categories_repo)],
    user_id: int | None = 1,
):
    current_categories = repo.read_all(user_id)

    current_categories = [x.name for x in current_categories]
    my_categories = deepcopy(CATEGORIES)
    name = my_categories[0]
    if name not in current_categories:
        add_category_to_db(session=session, name=name, user_id=user_id)
    my_categories.remove(name)
    for _ in range(len(my_categories)):
        choice = random.choice(my_categories)
        if choice not in current_categories:
            add_category_to_db(session=session, name=choice, user_id=user_id)
        my_categories.remove(choice)


@dev_router.post("/populate-payments")
def create_payments_in_db(
    session: Annotated[Session, Depends(get_session)],
    repo: Annotated[CategoryRepo, Depends(categories_repo)],
    user_id: int | None = 1,
):
    categories = repo.read_all(user_id)
    if not categories:
        for i in range(len(CATEGORIES)):
            add_category_to_db(
                session=session, name=CATEGORIES[i], user_id=user_id
            )
        categories = repo.read_all(user_id)
    category_ids = [x.id for x in categories]
    for _ in range(len(PRODUCTS)):
        add_payments_to_db(
            session, category_id=random.choice(category_ids), user_id=user_id
        )
