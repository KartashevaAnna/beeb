from typing import Annotated

import fastapi
from fastapi import Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from app.repositories.categories import CategoryRepo
from app.repositories.expenses import ExpenseRepo
from app.schemas.expenses import ExpenseCreate
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import categories_repo, expenses_repo

create_expenses_router = fastapi.APIRouter()


@create_expenses_router.get(SETTINGS.urls.create_expense)
def serve_create_expense_template(
    request: Request,
    repo: Annotated[ExpenseRepo, Depends(categories_repo)],
):
    return TEMPLATES.TemplateResponse(
        SETTINGS.templates.create_expense,
        context={
            "request": request,
            "options": repo.list_names(),
        },
    )


@create_expenses_router.post(SETTINGS.urls.create_expense)
def create_expense(
    name: Annotated[str, Form()],
    price: Annotated[str, Form()],
    category: Annotated[str, Form()],
    repo: Annotated[ExpenseRepo, Depends(expenses_repo)],
    category_repo: Annotated[CategoryRepo, Depends(categories_repo)],
    request: Request,
):
    try:
        options = category_repo.get_dict_names()

        new_expense = ExpenseCreate(
            name=name, price=price, category_id=options[category]
        )

        repo.create(new_expense)

        return RedirectResponse(
            SETTINGS.urls.create_expense,
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
