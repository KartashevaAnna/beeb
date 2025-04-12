import copy
import random
from typing import Annotated

import fastapi
from fastapi import Depends
from sqlalchemy.orm import Session

from app.repositories.categories import CategoryRepo
from app.utils.constants import CATEGORIES, PRODUCTS
from app.utils.dependencies import categories_repo, get_session
from app.utils.tools.helpers import add_category_to_db, add_expenses_to_db

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


@dev_router.post("/populate-expenses")
def create_expenses_in_db(
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
        add_expenses_to_db(session, category_id=random.choice(category_ids))
