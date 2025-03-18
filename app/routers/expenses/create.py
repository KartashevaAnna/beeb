from typing import Annotated

import fastapi
from fastapi import Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from app.repositories.expenses import ExpensesRepo
from app.schemas.expenses import ExpenseCreate
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import expenses_repo

create_expenses_router = fastapi.APIRouter()


@create_expenses_router.get(SETTINGS.urls.create_expense)
def serve_create_expense_template(request: Request):
    return TEMPLATES.TemplateResponse(
        SETTINGS.templates.create_expense,
        context={"request": request},
    )


@create_expenses_router.post(SETTINGS.urls.create_expense)
def create_expense(
    name: Annotated[str, Form()],
    price: Annotated[str, Form()],
    category: Annotated[str, Form()],
    repo: Annotated[ExpensesRepo, Depends(expenses_repo)],
    request: Request,
):
    try:
        new_expense = ExpenseCreate(name=name, price=price, category=category)
        created_expense = repo.create(new_expense)

        return RedirectResponse(
            SETTINGS.urls.expense.format(expense_id=created_expense.id),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    except ValidationError as exc:
        return TEMPLATES.TemplateResponse(
            SETTINGS.templates.create_expense,
            context={
                "request": request,
                "exception": f"Error: {str(exc)}",
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    except Exception as exc:
        return TEMPLATES.TemplateResponse(
            SETTINGS.templates.create_expense,
            context={
                "request": request,
                "exception": f"Error: {str(exc)}",
            },
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
        )
