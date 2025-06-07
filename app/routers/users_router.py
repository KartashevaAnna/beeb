from fastapi import APIRouter

from app.routers.users.create import create_users_router

users_router = APIRouter(tags=["Users"])
users_router.include_router(create_users_router)
