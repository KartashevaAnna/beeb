from typing import Annotated

import fastapi
from fastapi import Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from app.repositories.categories import CategoryRepo
from app.repositories.payments import PaymentRepo
from app.schemas.payments import PaymentCreate
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import categories_repo, payments_repo

create_payments_router = fastapi.APIRouter()


@create_payments_router.get(SETTINGS.urls.create_payment)
def serve_create_payment_template(
    request: Request,
    repo: Annotated[PaymentRepo, Depends(categories_repo)],
):
    return TEMPLATES.TemplateResponse(
        SETTINGS.templates.create_payment,
        context={
            "request": request,
            "options": repo.list_names(),
        },
    )


@create_payments_router.post(SETTINGS.urls.create_payment)
def create_payment(
    name: Annotated[str, Form()],
    price: Annotated[str, Form()],
    category: Annotated[str, Form()],
    repo: Annotated[PaymentRepo, Depends(payments_repo)],
    category_repo: Annotated[CategoryRepo, Depends(categories_repo)],
    request: Request,
):
    try:
        options = category_repo.get_dict_names()
        new_payment = PaymentCreate(
            name=name, price=price, category_id=options[category]
        )
        repo.create(new_payment)
        return RedirectResponse(
            SETTINGS.urls.create_payment,
            status_code=status.HTTP_303_SEE_OTHER,
        )

    except ValidationError as exc:
        return TEMPLATES.TemplateResponse(
            SETTINGS.templates.create_payment,
            context={
                "request": request,
                "exception": f"Error: {str(exc)}",
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    except Exception as exc:
        return TEMPLATES.TemplateResponse(
            SETTINGS.templates.create_payment,
            context={
                "request": request,
                "exception": f"Error: {str(exc)}",
            },
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
        )
