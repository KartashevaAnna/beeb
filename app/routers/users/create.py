from typing import Annotated

import fastapi
from fastapi import Depends, Form, Request, status
from fastapi.responses import RedirectResponse

from app.exceptions import BeebError, EmptyStringError
from app.repositories.users import UserRepo
from app.schemas.users import UserCreate
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import get_block_name, user_repo

create_users_router = fastapi.APIRouter()


@create_users_router.get(SETTINGS.urls.signup)
def signup_template(
    request: Request,
    block_name: Annotated[str | None, Depends(get_block_name)],
):
    return TEMPLATES.TemplateResponse(
        request=request,
        name=SETTINGS.templates.signup,
        block_name=block_name,
        context={"form_action": SETTINGS.urls.signup},
    )


@create_users_router.post(SETTINGS.urls.signup)
def create_user_in_db(
    repo: Annotated[UserRepo, Depends(user_repo)],
    block_name: Annotated[str | None, Depends(get_block_name)],
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    try:
        new_user = UserCreate(
            username=username,
            password=password,
        )

        repo.create(user=new_user)
        return RedirectResponse(
            SETTINGS.urls.login, status_code=status.HTTP_303_SEE_OTHER
        )
    except ValueError as exc:
        raise EmptyStringError(exc.args[0])
    except BeebError as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.home_page,
            context={
                "exception": exc.detail,
                "status_code": exc.status_code,
            },
            status_code=exc.status_code,
            block_name=block_name,
        )
