from typing import Annotated

import fastapi
from fastapi import Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from app.repositories.categories import CategoryRepo
from app.schemas.categories import CategoryCreate
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import categories_repo

create_categories_router = fastapi.APIRouter()


@create_categories_router.get(SETTINGS.urls.create_category)
def serve_create_category_template(
    request: Request,
):
    return TEMPLATES.TemplateResponse(
        SETTINGS.templates.create_category,
        context={
            "request": request,
        },
    )


@create_categories_router.post(SETTINGS.urls.create_category)
def create_category(
    name: Annotated[str, Form()],
    repo: Annotated[CategoryRepo, Depends(categories_repo)],
    request: Request,
):
    try:
        if new_category := repo.read_name(category_name=name):
            raise HTTPException(
                status.HTTP_406_NOT_ACCEPTABLE,
                "Category with this name already exists",
            )
        new_category = CategoryCreate(name=name)
        repo.create(new_category)
        return RedirectResponse(
            SETTINGS.urls.create_category,
            status_code=status.HTTP_303_SEE_OTHER,
        )
    except HTTPException as exc:
        return TEMPLATES.TemplateResponse(
            SETTINGS.templates.create_category,
            context={
                "request": request,
                "exception": f"Error: {str(exc)}",
            },
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
        )
    except ValidationError as exc:
        return TEMPLATES.TemplateResponse(
            SETTINGS.templates.create_category,
            context={
                "request": request,
                "exception": f"Error: {str(exc)}",
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    except Exception as exc:
        return TEMPLATES.TemplateResponse(
            SETTINGS.templates.create_category,
            context={
                "request": request,
                "exception": f"Error: {str(exc)}",
            },
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
        )
