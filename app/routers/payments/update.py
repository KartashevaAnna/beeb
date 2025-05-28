from typing import Annotated

import fastapi
from fastapi import Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from app.exceptions import BeebError
from app.repositories.categories import CategoryRepo
from app.repositories.payments import PaymentRepo
from app.routers.auth_router import authenticate
from app.schemas.payments import PaymentUpdate
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import categories_repo, payments_repo

update_payment_router = fastapi.APIRouter()


@update_payment_router.post(SETTINGS.urls.update_payment)
@authenticate
def update_payment(
    name: Annotated[str, Form()],
    amount: Annotated[str, Form()],
    category: Annotated[str, Form()],
    date: Annotated[str, Form()],
    payment_id: int,
    repo: Annotated[PaymentRepo, Depends(payments_repo)],
    category_repo: Annotated[CategoryRepo, Depends(categories_repo)],
    request: Request,
    user_id: int | None = None,
):
    try:
        options = category_repo.get_dict_names(user_id=user_id)
        to_update = PaymentUpdate(
            user_id=user_id,
            name=name,
            amount=amount,
            category_id=options[category],
            date=date,
        )
        repo.update(payment_id=payment_id, to_update=to_update)
        return RedirectResponse(
            url=SETTINGS.urls.payments, status_code=status.HTTP_303_SEE_OTHER
        )
    except BeebError as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.read_payment,
            context={
                "exception": exc.detail,
            },
            status_code=exc.status_code,
        )
    except Exception as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.read_payment,
            context={
                "exception": f"Ошибка: {str(exc)}",
            },
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
        )


@update_payment_router.get(SETTINGS.urls.update_payment)
@authenticate
def serve_update_payment_template(
    payment_id: int,
    repo: Annotated[PaymentRepo, Depends(payments_repo)],
    category_repo: Annotated[CategoryRepo, Depends(categories_repo)],
    request: Request,
    user_id: int | None = None,
):
    try:
        if not (payment := repo.read(payment_id)):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "payment not found")
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.read_payment,
            context={
                "payment": payment,
                "form_disabled": False,
                "options": category_repo.get_payments_options(
                    user_id=user_id, current_option=payment.category
                ),
                "form_action": SETTINGS.urls.update_payment_core,
            },
        )
    except HTTPException as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.read_payment,
            context={
                "exception": f"Ошибка: {str(exc)}",
            },
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except Exception as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.read_payment,
            context={
                "exception": f"Ошибка: {str(exc)}",
            },
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
        )
