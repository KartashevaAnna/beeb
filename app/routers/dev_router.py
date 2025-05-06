import copy
import locale
import os
import random
from typing import Annotated

import fastapi
from fastapi import Depends
from pyexcel_odsr import get_data
from sqlalchemy.orm import Session

from app.models import Payment
from app.repositories.categories import CategoryRepo
from app.repositories.payments import PaymentRepo
from app.schemas.categories import CategoryCreate
from app.settings import PAYMENTS_TO_UPLOAD_DIR
from app.utils.constants import CATEGORIES, PRODUCTS
from app.utils.dependencies import categories_repo, get_session, payments_repo
from app.utils.tools.category_helpers import (
    add_category_to_db,
)
from app.utils.tools.helpers import (
    add_payments_to_db,
    convert_to_copecks,
    get_date_for_database,
)

dev_router = fastapi.APIRouter(tags=["Dev"], include_in_schema=True)


@dev_router.post("/populate-categories")
def create_category_in_db(
    session: Annotated[Session, Depends(get_session)],
    repo: Annotated[CategoryRepo, Depends(categories_repo)],
):
    current_categories = repo.read_all()

    current_categories = [x.name for x in current_categories]
    my_categories = copy.deepcopy(CATEGORIES)
    name = my_categories[0]
    if name not in current_categories:
        add_category_to_db(session, name)
    my_categories.remove(name)
    for _ in range(len(my_categories)):
        choice = random.choice(my_categories)
        if choice not in current_categories:
            add_category_to_db(session, choice)
        my_categories.remove(choice)


@dev_router.post("/populate-payments")
def create_payments_in_db(
    session: Annotated[Session, Depends(get_session)],
    repo: Annotated[CategoryRepo, Depends(categories_repo)],
):
    categories = repo.read_all()
    if not categories:
        for i in range(len(CATEGORIES)):
            add_category_to_db(session, CATEGORIES[i])
        categories = repo.read_all()
    category_ids = [x.id for x in categories]
    for _ in range(len(PRODUCTS)):
        add_payments_to_db(session, category_id=random.choice(category_ids))


@dev_router.post("/upload-payments")
def upload_payments_from_ods_file(
    session: Annotated[Session, Depends(get_session)],
    category_repo: Annotated[CategoryRepo, Depends(categories_repo)],
    repo: Annotated[PaymentRepo, Depends(payments_repo)],
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
                category_name
            ) or category_repo.create(CategoryCreate(name=category_name))
            name = entry[0]
            price = convert_to_copecks(locale.atoi(entry[2][:3]))
            payment = Payment(
                name=name, price=price, category_id=category.id, created_at=date
            )
            session.add(payment)
    session.commit()

    return repo.read_all()
