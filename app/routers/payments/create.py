from datetime import datetime
from typing import Annotated

import fastapi
from fastapi import Depends, Form, Request, status
from fastapi.responses import RedirectResponse

from app.exceptions import BeebError
from app.repositories.categories import CategoryRepo
from app.repositories.payments import PaymentRepo
from app.routers.auth_router import authenticate
from app.schemas.payments import PaymentCreate
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import (
    categories_repo,
    payments_repo,
)

create_payments_router = fastapi.APIRouter()


@create_payments_router.get(SETTINGS.urls.create_payment)
@authenticate
def serve_create_payment_template(
    request: Request,
    repo: Annotated[PaymentRepo, Depends(categories_repo)],
    user_id: int | None = None,
):
    return TEMPLATES.TemplateResponse(
        request,
        SETTINGS.templates.create_payment,
        context={
            "options": repo.list_names(user_id=user_id),
        },
    )


@create_payments_router.post(SETTINGS.urls.create_payment)
@authenticate
def create_payment(
    name: Annotated[str, Form()],
    price: Annotated[str, Form()],
    category: Annotated[str, Form()],
    repo: Annotated[PaymentRepo, Depends(payments_repo)],
    category_repo: Annotated[CategoryRepo, Depends(categories_repo)],
    request: Request,
    is_spending: bool = Form(False),
    user_id: int | None = None,
):
    try:
        options = category_repo.get_dict_names(user_id=user_id)
        new_payment = PaymentCreate(
            user_id=user_id,
            name=name,
            price_in_rub=price,
            category_id=options[category],
            created_at=datetime.now(),
            is_spending=is_spending,
        )
        repo.create(new_payment)
        return RedirectResponse(
            SETTINGS.urls.create_payment,
            status_code=status.HTTP_303_SEE_OTHER,
        )
    except BeebError as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.create_payment,
            context={
                "exception": exc.detail,
                "status_code": exc.status_code,
            },
            status_code=exc.status_code,
        )
    except Exception as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.create_payment,
            context={
                "exception": f"Ошибка: {str(exc)}",
            },
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
        )
