from datetime import datetime
from typing import Annotated, Optional
import fastapi
from fastapi import Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from app.exceptions import BeebError
from app.repositories.income import IncomeRepo
from app.routers.auth_router import authenticate
from app.schemas.income import IncomeCreate
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import income_repo


create_income_router = fastapi.APIRouter()


@create_income_router.get(SETTINGS.urls.create_income)
@authenticate
def serve_create_income_template(
    request: fastapi.Request,
    user_id: int | None = None,
):
    return TEMPLATES.TemplateResponse(
        request,
        SETTINGS.templates.create_income,
        context={"form_action": SETTINGS.urls.create_income},
    )


@create_income_router.post(SETTINGS.urls.create_income)
@authenticate
def create_income(
    name: Annotated[str, Form()],
    amount: Annotated[str, Form()],
    repo: Annotated[IncomeRepo, Depends(income_repo)],
    request: Request,
    user_id: int | None = None,
):
    try:
        new_income = IncomeCreate(
            user_id=user_id,
            name=name,
            amount_in_rub=amount,
            created_at=datetime.now(),
        )
        repo.create(income=new_income, user_id=user_id)

        return RedirectResponse(
            SETTINGS.urls.payments,
            status_code=status.HTTP_303_SEE_OTHER,
        )

    except BeebError as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.create_income,
            context={
                "exception": exc.detail,
            },
            status_code=exc.status_code,
        )

    except Exception as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.create_income,
            context={
                "exception": f"Ошибка: {str(exc)}",
            },
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
        )
