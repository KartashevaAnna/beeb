from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from app.exceptions import BeebError
from app.repositories.categories import CategoryRepo
from app.routers.auth_router import authenticate
from app.schemas.categories import CategoryCreate
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import categories_repo

create_categories_router = APIRouter()


@create_categories_router.get(SETTINGS.urls.create_category)
@authenticate
def serve_create_category_template(
    request: Request,
    user_id: int | None = None,
):
    return TEMPLATES.TemplateResponse(
        request,
        SETTINGS.templates.create_category,
        context={"form_action": SETTINGS.urls.create_category},
    )


@create_categories_router.post(SETTINGS.urls.create_category)
@authenticate
def create_category(
    name: Annotated[str, Form()],
    repo: Annotated[CategoryRepo, Depends(categories_repo)],
    request: Request,
    user_id: int | None = None,
):
    try:
        new_category = CategoryCreate(name=name, user_id=user_id)
        repo.create(new_category)
        return RedirectResponse(
            SETTINGS.urls.categories,
            status_code=status.HTTP_303_SEE_OTHER,
        )
    except BeebError as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.create_category,
            context={
                "exception": exc.detail,
            },
            status_code=exc.status_code,
        )
    except ValidationError as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.create_category,
            context={
                "exception": f"Ошибка: {str(exc)}",
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    except Exception as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.create_category,
            context={
                "exception": f"Ошибка: {str(exc)}",
            },
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
        )
