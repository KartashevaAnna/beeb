from typing import Annotated

import fastapi
from fastapi import Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from app.repositories.categories import CategoryRepo
from app.repositories.payments import PaymentRepo
from app.schemas.payments import PaymentUpdate
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import categories_repo, payments_repo

update_payment_router = fastapi.APIRouter()


@update_payment_router.post(SETTINGS.urls.update_payment)
def update_payment(
    name: Annotated[str, Form()],
    price: Annotated[str, Form()],
    category: Annotated[str, Form()],
    date: Annotated[str, Form()],
    payment_id: int,
    repo: Annotated[PaymentRepo, Depends(payments_repo)],
    category_repo: Annotated[CategoryRepo, Depends(categories_repo)],
    request: Request,
):
    try:
        options = category_repo.get_dict_names()
        to_update = PaymentUpdate(
            name=name,
            price=price,
            category_id=options[category],
            date=date,
        )
        repo.update(payment_id=payment_id, to_upate=to_update)
        return RedirectResponse(
            url=SETTINGS.urls.payments, status_code=status.HTTP_303_SEE_OTHER
        )
    except Exception as exc:
        return TEMPLATES.TemplateResponse(
            SETTINGS.templates.read_payment,
            context={
                "request": request,
                "exception": f"There was an error: {str(exc)}",
            },
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
        )


@update_payment_router.get(SETTINGS.urls.update_payment)
def serve_update_payment_template(
    payment_id: int,
    repo: Annotated[PaymentRepo, Depends(payments_repo)],
    category_repo: Annotated[CategoryRepo, Depends(categories_repo)],
    request: Request,
):
    try:
        if not (payment := repo.read(payment_id)):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "payment not found")
        return TEMPLATES.TemplateResponse(
            SETTINGS.templates.read_payment,
            context={
                "request": request,
                "payment": payment,
                "form_disabled": False,
                "options": category_repo.get_payments_options(
                    current_option=payment.category
                ),
            },
        )
    except HTTPException as exc:
        return TEMPLATES.TemplateResponse(
            SETTINGS.templates.read_payment,
            context={
                "request": request,
                "exception": f"There was an error: {str(exc)}",
            },
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except Exception as exc:
        return TEMPLATES.TemplateResponse(
            SETTINGS.templates.read_payment,
            context={
                "request": request,
                "exception": f"There was an error: {str(exc)}",
            },
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
        )
