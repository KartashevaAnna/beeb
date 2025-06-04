from dataclasses import Field
from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter
from fastapi import Depends, Form, Request, status
from fastapi.responses import RedirectResponse

from app.exceptions import BeebError
from app.repositories.categories import CategoryRepo
from app.repositories.payments import PaymentRepo
from app.routers.auth_router import authenticate
from app.schemas.payments import PaymentCreate
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import categories_repo, payments_repo

create_payments_router = APIRouter()


@create_payments_router.get(SETTINGS.urls.select_food_non_food)
@authenticate
def serve_select_food_non_food_template(
    request: Request,
    user_id: int | None = None,
):
    return TEMPLATES.TemplateResponse(
        request,
        SETTINGS.templates.select_food_non_food,
        context={
            "create_food": SETTINGS.urls.create_payment_food,
            "create_non_food": SETTINGS.urls.create_payment_non_food,
        },
    )


@create_payments_router.get(SETTINGS.urls.select_income_expense)
@authenticate
def serve_select_income_expense_template(
    request: Request,
    user_id: int | None = None,
):
    return TEMPLATES.TemplateResponse(
        request,
        SETTINGS.templates.select_income_expense,
        context={
            "create_income": SETTINGS.urls.create_income,
            "create_expense": SETTINGS.urls.select_food_non_food,
        },
    )


@create_payments_router.get(SETTINGS.urls.create_payment_food)
@authenticate
def serve_create_food_template(
    request: Request,
    repo: Annotated[PaymentRepo, Depends(categories_repo)],
    user_id: int | None = None,
):
    return TEMPLATES.TemplateResponse(
        request,
        SETTINGS.templates.create_payment_food,
        context={
            "options": repo.list_names(user_id=user_id),
            "form_action": SETTINGS.urls.create_payment,
        },
    )


@create_payments_router.get(SETTINGS.urls.create_payment_non_food)
@authenticate
def serve_create_non_food_template(
    request: Request,
    repo: Annotated[PaymentRepo, Depends(categories_repo)],
    user_id: int | None = None,
):
    return TEMPLATES.TemplateResponse(
        request,
        SETTINGS.templates.create_payment_non_food,
        context={
            "options": repo.list_names(user_id=user_id),
            "form_action": SETTINGS.urls.create_payment,
        },
    )


@create_payments_router.post(SETTINGS.urls.create_payment)
@authenticate
def create_payment(
    name: Annotated[str, Form()],
    amount: Annotated[str, Form()],
    category: Annotated[str, Form()],
    repo: Annotated[PaymentRepo, Depends(payments_repo)],
    category_repo: Annotated[CategoryRepo, Depends(categories_repo)],
    request: Request,
    user_id: int | None = None,
    grams: Optional[str] = Form(None),
    quantity: Optional[str] = Form(None),
):
    if grams:
        url = SETTINGS.templates.create_payment_food
    else:
        url = SETTINGS.templates.create_payment_non_food
    try:
        options = category_repo.get_dict_names(user_id=user_id)
        new_payment = PaymentCreate(
            user_id=user_id,
            name=name,
            amount_in_rub=amount,
            category_id=options[category],
            created_at=datetime.now(),
            grams=grams,
            quantity=quantity,
        )
        repo.create(payment=new_payment, user_id=user_id)
        if grams:
            return RedirectResponse(
                SETTINGS.urls.create_payment_food,
                status_code=status.HTTP_303_SEE_OTHER,
            )
        else:
            return RedirectResponse(
                SETTINGS.urls.create_payment_non_food,
                status_code=status.HTTP_303_SEE_OTHER,
            )
    except BeebError as exc:
        return TEMPLATES.TemplateResponse(
            request,
            url,
            context={
                "exception": exc.detail,
            },
            status_code=exc.status_code,
        )

    except Exception as exc:
        return TEMPLATES.TemplateResponse(
            request,
            url,
            context={
                "exception": f"Ошибка: {str(exc)}",
            },
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
        )
