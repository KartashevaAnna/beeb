from copy import deepcopy
import csv
import locale
import os
import random
from typing import Annotated
from fastapi import APIRouter

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


@dev_router.post("/upload-payments")
def upload_payments_from_csv(
    session: Annotated[Session, Depends(get_session)],
    category_repo: Annotated[CategoryRepo, Depends(categories_repo)],
    repo: Annotated[PaymentRepo, Depends(payments_repo)],
    user_id: int | None = 1,
):
    filenames = os.listdir(PAYMENTS_TO_UPLOAD_DIR)
    for file in filenames:
        with open(f"{PAYMENTS_TO_UPLOAD_DIR}/{file}", newline="") as f:
            reader = csv.reader(f)
            filename = file[:-4]
            date = get_date_for_database(filename)
            for row in reader:
                category_name = row[1].lower()
                if category_name == "еда":
                    category_name = "продукты"
                if len(category_name) != 0:
                    category = CategoryRepo(session).read_name(
                        user_id=user_id, category_name=category_name
                    ) or category_repo.create(
                        CategoryCreate(
                            user_id=user_id, name=category_name, is_active=True
                        ),
                    )
                    name = row[0]
                    amount = get_number_for_db(row[2].replace(",", ""))
                    payment = Payment(
                        user_id=user_id,
                        name=name,
                        amount=amount,
                        category_id=category.id,
                        created_at=date,
                    )
                    session.add(payment)
    session.commit()

    return repo.read_all(user_id)
