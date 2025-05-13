from typing import Annotated

import fastapi
from fastapi import Depends, Request, status

from app.repositories.categories import CategoryRepo
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import categories_repo

read_categories_router = fastapi.APIRouter()


@read_categories_router.get(SETTINGS.urls.categories)
def read_all(
    repo: Annotated[CategoryRepo, Depends(categories_repo)],
    request: Request,
):
    try:
        categories = repo.read_all()
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.read_categories,
            context={"categories": categories},
        )
    except Exception as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.read_categories,
            context={
                "payments": [],
                "exception": f"There was an error: {str(exc)}",
            },
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
        )
