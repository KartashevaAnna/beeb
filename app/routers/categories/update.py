from typing import Annotated

import fastapi
from fastapi import Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from app.repositories.categories import CategoryRepo
from app.schemas.categories import CategoryCreate
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import categories_repo

update_category_router = fastapi.APIRouter()


@update_category_router.get(SETTINGS.urls.update_category)
def serve_update_category_template(
    category_id: int,
    repo: Annotated[CategoryRepo, Depends(categories_repo)],
    request: Request,
):
    try:
        if not (category := repo.read(category_id)):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")
        return TEMPLATES.TemplateResponse(
            SETTINGS.templates.read_category,
            context={
                "request": request,
                "category": category,
                "form_disabled": False,
                "options": repo.get_status_options(
                    current_option=category.is_active
                ),
            },
        )
    except HTTPException as exc:
        return TEMPLATES.TemplateResponse(
            SETTINGS.templates.read_category,
            context={
                "request": request,
                "exception": f"There was an error: {str(exc)}",
            },
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except Exception as exc:
        return TEMPLATES.TemplateResponse(
            SETTINGS.templates.read_category,
            context={
                "request": request,
                "exception": f"There was an error: {str(exc)}",
            },
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
        )


@update_category_router.post(SETTINGS.urls.update_category)
def update_category(
    name: Annotated[str, Form()],
    category_id: int,
    repo: Annotated[CategoryRepo, Depends(categories_repo)],
    request: Request,
    is_active: bool = Form(False),
):
    try:
        to_update = CategoryCreate(name=name, is_active=is_active)
        category_with_the_same_name = repo.read_name(name)
        if category_with_the_same_name:
            if category_with_the_same_name.id != category_id:
                raise HTTPException(
                    status.HTTP_304_NOT_MODIFIED,
                    "Category with this name already exists",
                )
        repo.update(category_id=category_id, to_update=to_update)
        return RedirectResponse(
            url="/categories", status_code=status.HTTP_303_SEE_OTHER
        )
    except HTTPException:
        return TEMPLATES.TemplateResponse(
            SETTINGS.templates.read_category,
            context={
                "request": request,
                "exception": "Категория с таким названием уже существует",
            },
            status_code=status.HTTP_304_NOT_MODIFIED,
        )
    except ValidationError as exc:
        return TEMPLATES.TemplateResponse(
            SETTINGS.templates.read_category,
            context={
                "request": request,
                "exception": f"There was an error: {str(exc)}",
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    except Exception as exc:
        return TEMPLATES.TemplateResponse(
            SETTINGS.templates.read_category,
            context={
                "request": request,
                "exception": f"There was an error: {str(exc)}",
            },
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
        )
