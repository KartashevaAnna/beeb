from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends, Request, status

from app.repositories.categories import CategoryRepo
from app.routers.auth_router import authenticate
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import categories_repo

read_categories_router = APIRouter()


@read_categories_router.get(SETTINGS.urls.categories)
@authenticate
def read_all(
    repo: Annotated[CategoryRepo, Depends(categories_repo)],
    request: Request,
    user_id: int | None = None,
):
    try:
        categories = repo.read_all(user_id=user_id)
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.read_categories,
            context={
                "categories": categories,
                "create": SETTINGS.urls.create_category,
                "update": SETTINGS.urls.update_category_core,
            },
        )
    except Exception as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.read_categories,
            context={
                "payments": [],
                "exception": f"Ошибка: {str(exc)}",
            },
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
        )
