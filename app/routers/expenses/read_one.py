from typing import Annotated

import fastapi
from fastapi import Depends, HTTPException, Request, status

from app.repositories.expenses import ExpensesRepo
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import expenses_repo

read_expense_router = fastapi.APIRouter()


@read_expense_router.get(SETTINGS.urls.expense)
def read_expense(
    expense_id: int,
    repo: Annotated[ExpensesRepo, Depends(expenses_repo)],
    request: Request,
):
    try:
        if not (expense := repo.read(expense_id)):
            raise HTTPException(404, "Expense not found")
        return TEMPLATES.TemplateResponse(
            SETTINGS.templates.read_expense,
            context={
                "request": request,
                "expense": expense,
                "form_disabled": True,
            },
        )
    except HTTPException as exc:
        return TEMPLATES.TemplateResponse(
            SETTINGS.templates.read_expense,
            context={
                "request": request,
                "exception": f"There was an error: {str(exc)}",
            },
            status_code=status.HTTP_404_NOT_FOUND,
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
