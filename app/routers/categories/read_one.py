from typing import Annotated

import fastapi
from fastapi import Depends, HTTPException, Request, status

from app.repositories.categories import CategoryRepo
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import categories_repo

read_category_router = fastapi.APIRouter()


@read_category_router.get(SETTINGS.urls.category)
def read_category(
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
                "form_disabled": True,
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
