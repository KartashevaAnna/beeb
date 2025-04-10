from typing import Annotated

import fastapi
from fastapi import Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse

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
            raise HTTPException(404, "Category not found")
        return TEMPLATES.TemplateResponse(
            SETTINGS.templates.read_category,
            context={
                "request": request,
                "category": category,
                "form_disabled": False,
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
):
    try:
        to_update = CategoryCreate(
            name=name,
        )
        if repo.read_name(name):
            raise HTTPException(406, "Category with this name already exists")
        repo.update(category_id=category_id, to_upate=to_update)
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
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
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
