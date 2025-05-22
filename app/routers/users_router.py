import fastapi

from app.routers.users.create import create_users_router

users_router = fastapi.APIRouter(tags=["Users"])
users_router.include_router(create_users_router)
