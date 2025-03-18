from typing import Annotated

import fastapi
from fastapi import Depends, Request, status
from fastapi.responses import RedirectResponse

from app.repositories.expenses import ExpensesRepo
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import expenses_repo

delete_expenses_router = fastapi.APIRouter()


@delete_expenses_router.get(SETTINGS.urls.delete_expense)
def delete_template(
    request: Request,
):
    return TEMPLATES.TemplateResponse(
        SETTINGS.templates.delete_expense,
        context={"request": request},
    )


@delete_expenses_router.post(SETTINGS.urls.delete_expense)
def delete_expense(
    expense_id: int,
    repo: Annotated[ExpensesRepo, Depends(expenses_repo)],
    request: Request,
):
    try:
        repo.delete(expense_id)
        return RedirectResponse(
            url="/expenses", status_code=status.HTTP_303_SEE_OTHER
        )
    except Exception as exc:
        return TEMPLATES.TemplateResponse(
            SETTINGS.templates.read_expense,
            context={
                "request": request,
                "exception": f"There was an error: {str(exc)}",
            },
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
        )
