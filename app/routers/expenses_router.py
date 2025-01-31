from typing import Annotated

import fastapi
from fastapi import Depends

from app.repositories.expenses import ExpenseRepo
from app.settings import SETTINGS
from app.utils.dependencies import expenses_repo

expenses_router = fastapi.APIRouter(tags=["Expenses"])


@expenses_router.get(SETTINGS.urls.expenses)
def read_all(repo: Annotated[ExpenseRepo, Depends(expenses_repo)]):
    try:
        return repo.read_all()
    except Exception as exc:
        return f"Exception: There was an error: {str(exc)}"
