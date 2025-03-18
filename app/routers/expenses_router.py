from typing import Annotated

import fastapi
from fastapi import Depends, Form, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from app.repositories.expenses import ExpensesRepo
from app.schemas.expenses import ExpenseCreate, ExpenseUpdate
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import expenses_repo
from app.utils.tools.helpers import get_expenses_options

expenses_router = fastapi.APIRouter(tags=["Expenses"])


@expenses_router.get(SETTINGS.urls.create_expense)
def serve_create_expense_template(request: Request):
    return TEMPLATES.TemplateResponse(
        SETTINGS.templates.create_expense,
        context={"request": request},
    )


@expenses_router.post(SETTINGS.urls.update_expense)
def update_expense(
    name: Annotated[str, Form()],
    price: Annotated[str, Form()],
    category: Annotated[str, Form()],
    expense_id: int,
    repo: Annotated[ExpensesRepo, Depends(expenses_repo)],
    request: Request,
):
    to_update = ExpenseUpdate(name=name, price=price, category=category)
    try:
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


@expenses_router.get(SETTINGS.urls.update_expense)
def serve_update_expense_template(
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
                "form_disabled": False,
                "options": get_expenses_options(expense.category),
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


@expenses_router.post(SETTINGS.urls.delete_expense)
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


@expenses_router.get(SETTINGS.urls.delete_expense)
def signup_template(
    request: Request,
):
    return TEMPLATES.TemplateResponse(
        SETTINGS.templates.delete_expense,
        context={"request": request},
    )


@expenses_router.get(SETTINGS.urls.expense)
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


@expenses_router.post(SETTINGS.urls.create_expense)
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


@expenses_router.get(SETTINGS.urls.expenses)
def read_all(
    repo: Annotated[ExpensesRepo, Depends(expenses_repo)],
    request: Request,
    response: Response,
):
    try:
        expenses = repo.read_all()
        total = repo.get_total()
        return TEMPLATES.TemplateResponse(
            SETTINGS.templates.read_expenses,
            context={"request": request, "expenses": expenses, "total": total},
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
