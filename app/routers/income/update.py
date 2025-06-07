from typing import Annotated
from fastapi import APIRouter, Form
from fastapi import status, Request, Depends
from fastapi.responses import RedirectResponse
from app.exceptions import BeebError, IncomeNotFoundError
from app.repositories.income import IncomeRepo
from app.routers.auth_router import authenticate
from app.schemas.income import IncomeUpdate
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import income_repo


update_income_router = APIRouter()


@update_income_router.get(SETTINGS.urls.update_income)
@authenticate
def serve_update_income_template(
    request: Request,
    income_id: int,
    repo: Annotated[IncomeRepo, Depends(income_repo)],
    user_id: int | None = None,
):
    if not (income := repo.read(income_id)):
        raise IncomeNotFoundError(income_id)
    return TEMPLATES.TemplateResponse(
        request,
        SETTINGS.templates.update_income,
        context={
            "income": income,
            "income_id": income_id,
            "update": SETTINGS.urls.update_income_core,
        },
    )


@update_income_router.post(SETTINGS.urls.update_income)
@authenticate
def update_income(
    request: Request,
    repo: Annotated[IncomeRepo, Depends(income_repo)],
    to_update: Annotated[IncomeUpdate, Form()],
    income_id: int,
    user_id: int | None = None,
):
    try:
        repo.update(income_id=income_id, user_id=user_id, to_update=to_update)
        return RedirectResponse(
            url=SETTINGS.urls.payments,
            status_code=status.HTTP_303_SEE_OTHER,
        )
    except BeebError as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.update_income,
            context={
                "exception": exc.detail,
            },
            status_code=exc.status_code,
        )
    except Exception as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.update_income,
            context={
                "exception": f"Ошибка: {str(exc)}",
            },
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
        )
