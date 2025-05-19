from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse

from app.exceptions import BeebError
from app.models import User
from app.repositories.users import UserRepo
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import get_block_name, user_repo
from app.utils.tools.auth_handler import AuthHandler

auth_router = APIRouter(tags=["Auth"])


@auth_router.get(SETTINGS.urls.login)
def serve_login_template(
    request: Request,
):
    return TEMPLATES.TemplateResponse(
        request,
        SETTINGS.templates.login,
    )


@auth_router.post(
    SETTINGS.urls.login,
)
def login(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    repo: Annotated[UserRepo, Depends(user_repo)],
    block_name: Annotated[str | None, Depends(get_block_name)],
    request: Request,
) -> RedirectResponse:
    try:
        user: User = repo.login(username, password)
    except BeebError as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.login,
            context={
                "exception": exc.detail,
                "status_code": exc.status_code,
            },
            block_name=block_name,
            status_code=exc.status_code,
        )
    except Exception as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.login,
            context={
                "exception": f"Ошибка: {str(exc)}",
                "status_code": status.HTTP_501_NOT_IMPLEMENTED,
            },
            block_name=block_name,
        )
    response = RedirectResponse(
        SETTINGS.urls.home_page, status_code=status.HTTP_303_SEE_OTHER
    )
    AuthHandler().set_cookies(
        response=response, username=user.username, id=user.id
    )
    return response
