from typing import Annotated

import fastapi
from fastapi import Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from app.repositories.categories import CategoryRepo
from app.repositories.expenses import ExpensesRepo
from app.schemas.expenses import ExpenseUpdate
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import categories_repo, expenses_repo

update_expenses_router = fastapi.APIRouter()


@update_expenses_router.post(SETTINGS.urls.update_expense)
def update_expense(
    name: Annotated[str, Form()],
    price: Annotated[str, Form()],
    category: Annotated[str, Form()],
    expense_id: int,
    repo: Annotated[ExpensesRepo, Depends(expenses_repo)],
    category_repo: Annotated[CategoryRepo, Depends(categories_repo)],
    request: Request,
):
    try:
        options = category_repo.get_dict_names()
        to_update = ExpenseUpdate(
            name=name, price=price, category_id=options[category]
        )
        repo.update(expense_id=expense_id, to_upate=to_update)
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


@update_expenses_router.get(SETTINGS.urls.update_expense)
def serve_update_expense_template(
    expense_id: int,
    repo: Annotated[ExpensesRepo, Depends(expenses_repo)],
    category_repo: Annotated[CategoryRepo, Depends(categories_repo)],
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
                "form_disabled": False,
                "options": category_repo.get_expenses_options(
                    current_option=expense.category
                ),
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
