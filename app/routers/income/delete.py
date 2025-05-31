from typing import Annotated

import fastapi
from fastapi import Depends, Request, status
from fastapi.responses import RedirectResponse

from app.exceptions import BeebError
from app.repositories.income import IncomeRepo
from app.routers.auth_router import authenticate
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import income_repo

delete_income_router = fastapi.APIRouter()


@delete_income_router.post(SETTINGS.urls.delete_income)
@authenticate
def delete_income(
    income_id: int,
    repo: Annotated[IncomeRepo, Depends(income_repo)],
    request: Request,
    user_id: int | None = None,
):
    try:
        repo.delete(income_id=income_id, user_id=user_id)
        return RedirectResponse(
            url=SETTINGS.urls.payments, status_code=status.HTTP_303_SEE_OTHER
        )
    except BeebError as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.delete_payment,
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


# "POST /payments/delete/23 HTTP/1.1" 303 See Other
# "POST /income/delete/2 HTTP/1.1" 404 Not Found
