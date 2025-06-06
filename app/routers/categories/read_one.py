from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends, HTTPException, Request, status

from app.repositories.categories import CategoryRepo
from app.routers.auth_router import authenticate
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import categories_repo

read_category_router = APIRouter()


@read_category_router.get(SETTINGS.urls.category)
@authenticate
def read_category(
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
