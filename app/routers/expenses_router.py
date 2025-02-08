from typing import Annotated

import fastapi
from fastapi import Depends, HTTPException, Request, Response, status

from app.repositories.expenses import ExpensesRepo
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import expenses_repo

expenses_router = fastapi.APIRouter(tags=["Expenses"])


@expenses_router.get(SETTINGS.urls.expense)
def read_expense(expense_id: int, repo: Annotated[ExpensesRepo, Depends(expenses_repo)], request: Request):
    try:
        if not (expense := repo.read(expense_id)):
            raise HTTPException(404, "Expense not found")
        return TEMPLATES.TemplateResponse(
            SETTINGS.templates.read_expense,
            context={"request": request, "expense": expense},
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


@expenses_router.get(SETTINGS.urls.expenses)
def read_all(repo: Annotated[ExpensesRepo, Depends(expenses_repo)], request: Request, response: Response):
    try:
        expenses = repo.read_all()
        return TEMPLATES.TemplateResponse(
            SETTINGS.templates.read_expenses, context={"request": request, "expenses": expenses}
        )
    except Exception as exc:
        return TEMPLATES.TemplateResponse(
            SETTINGS.templates.read_expenses,
            context={
                "request": request,
                "expenses": [],
                "exception": f"There was an error: {str(exc)}",
            },
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
        )
