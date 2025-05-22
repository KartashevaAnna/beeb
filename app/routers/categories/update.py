from typing import Annotated

import fastapi
from fastapi import Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from app.exceptions import BeebError, DuplicateNameEditError
from app.repositories.categories import CategoryRepo
from app.routers.auth_router import authenticate
from app.schemas.categories import CategoryCreate
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import categories_repo

update_category_router = fastapi.APIRouter()


@update_category_router.get(SETTINGS.urls.update_category)
@authenticate
def serve_update_category_template(
    category_id: int,
    repo: Annotated[CategoryRepo, Depends(categories_repo)],
    request: Request,
    user_id: int | None = None,
):
    try:
        if not (category := repo.read(category_id)):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.read_category,
            context={
                "category": category,
                "form_disabled": False,
                "options": repo.get_status_options(
                    current_option=category.is_active
                ),
            },
        )
    except HTTPException as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.read_category,
            context={
                "exception": f"Ошибка: {str(exc)}",
            },
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except Exception as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.read_category,
            context={
                "exception": f"Ошибка: {str(exc)}",
            },
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
        )


@update_category_router.post(SETTINGS.urls.update_category)
@authenticate
def update_category(
    name: Annotated[str, Form()],
    category_id: int,
    repo: Annotated[CategoryRepo, Depends(categories_repo)],
    request: Request,
    is_active: bool = Form(False),
    user_id: int | None = None,
):
    try:
        to_update = CategoryCreate(
            name=name, is_active=is_active, user_id=user_id
        )
        category_with_the_same_name = repo.read_name(name, user_id=user_id)
        if category_with_the_same_name:
            if category_with_the_same_name.id != category_id:
                raise DuplicateNameEditError(category_with_the_same_name.name)
        repo.update(category_id=category_id, to_update=to_update)
        return RedirectResponse(
            url=SETTINGS.urls.categories, status_code=status.HTTP_303_SEE_OTHER
        )
    except BeebError as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.read_payment,
            context={
                "exception": exc.detail,
                "status_code": exc.status_code,
            },
            status_code=exc.status_code,
        )
    except ValidationError as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.read_category,
            context={
                "exception": f"Ошибка: {str(exc)}",
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    except Exception as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.read_category,
            context={
                "exception": f"Ошибка: {str(exc)}",
            },
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
        )
