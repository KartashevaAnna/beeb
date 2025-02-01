from typing import Annotated

import fastapi
from fastapi import Depends, Request

from app.repositories.expenses import ExpenseRepo
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import expenses_repo

expenses_router = fastapi.APIRouter(tags=["Expenses"])


@expenses_router.get(SETTINGS.urls.expenses)
def read_all(repo: Annotated[ExpenseRepo, Depends(expenses_repo)], request: Request):
    try:
        expenses = repo.read_all()
        return TEMPLATES.TemplateResponse(
            SETTINGS.templates.read_expenses, context={"request": request, "expenses": expenses}
        )
    except Exception as exc:
        return f"Exception: There was an error: {str(exc)}"
