import copy
import locale
import os
import random
from typing import Annotated

import fastapi
from fastapi import Depends, Request
from pyexcel_odsr import get_data
from sqlalchemy.orm import Session

from app.models import Payment
from app.repositories.categories import CategoryRepo
from app.repositories.payments import PaymentRepo
from app.routers.auth_router import authenticate
from app.schemas.categories import CategoryCreate
from app.settings import PAYMENTS_TO_UPLOAD_DIR
from app.utils.constants import CATEGORIES, PRODUCTS
from app.utils.dependencies import categories_repo, get_session, payments_repo
from app.utils.tools.category_helpers import add_category_to_db
from app.utils.tools.helpers import (
    add_payments_to_db,
    convert_to_copecks,
    get_date_for_database,
)

dev_router = fastapi.APIRouter(tags=["Dev"], include_in_schema=True)


@dev_router.post("/populate-categories")
@authenticate
def create_category_in_db(
    request: Request,
    session: Annotated[Session, Depends(get_session)],
    repo: Annotated[CategoryRepo, Depends(categories_repo)],
    user_id: int | None = None,
):
    current_categories = repo.read_all(user_id)

    current_categories = [x.name for x in current_categories]
    my_categories = copy.deepcopy(CATEGORIES)
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
@authenticate
def create_payments_in_db(
    request: Request,
    session: Annotated[Session, Depends(get_session)],
    repo: Annotated[CategoryRepo, Depends(categories_repo)],
    user_id: int | None = None,
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


@dev_router.post("/upload-payments")
@authenticate
def upload_payments_from_libreoffice_calc_file(
    request: Request,
    session: Annotated[Session, Depends(get_session)],
    category_repo: Annotated[CategoryRepo, Depends(categories_repo)],
    repo: Annotated[PaymentRepo, Depends(payments_repo)],
    user_id: int | None = None,
):
    filenames = os.listdir(PAYMENTS_TO_UPLOAD_DIR)
    for file in filenames:
        filename = file[:-4]
        data = get_data(f"{PAYMENTS_TO_UPLOAD_DIR}/{file}")
        date = get_date_for_database(filename)
        uploaded_payments = data["Массив данных"]
        not_null_payments = [x for x in uploaded_payments if len(x) > 0]

        for entry in not_null_payments:
            category_name = entry[1].lower()
            if category_name == "еда":
                category_name = "продукты"
            category = CategoryRepo(session).read_name(
                user_id=user_id, category_name=category_name
            ) or category_repo.create(
                CategoryCreate(
                    user_id=user_id, name=category_name, is_active=True
                )
            )
            name = entry[0]
            price = convert_to_copecks(locale.atoi(entry[2][:3]))
            payment = Payment(
                user_id=user_id,
                name=name,
                price=price,
                category_id=category.id,
                created_at=date,
            )
            session.add(payment)
    session.commit()

    return repo.read_all(user_id)
