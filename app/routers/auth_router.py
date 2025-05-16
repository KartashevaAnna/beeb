from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from app.settings import SETTINGS, TEMPLATES

auth_router = APIRouter(tags=["Auth"])


@auth_router.get(SETTINGS.urls.login)
def serve_login_template(
    request: Request,
):
    return TEMPLATES.TemplateResponse(
        request,
        SETTINGS.templates.login,
    )


@auth_router.post(
    SETTINGS.urls.login,
)
def login(
    request: Request,
) -> RedirectResponse:
    return 200
