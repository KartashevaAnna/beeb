from typing import Annotated

from fastapi import Cookie, Depends, Header
from sqlalchemy.orm import Session, sessionmaker

from app.repositories.categories import CategoryRepo
from app.repositories.payments import PaymentRepo
from app.repositories.users import UserRepo
from app.settings import ENGINE
from app.utils.tools.auth_handler import AuthHandler


def get_session():
    session = sessionmaker(bind=ENGINE)
    try:
        yield (session := session())
    finally:
        session.close()


def user_repo(session: Session = Depends(get_session)) -> UserRepo:
    return UserRepo(session)


def payments_repo(session: Session = Depends(get_session)) -> PaymentRepo:
    return PaymentRepo(session)


def categories_repo(session: Session = Depends(get_session)) -> CategoryRepo:
    return CategoryRepo(session)


def get_block_name(hx_request: Annotated[str | None, Header()] = None):
    return "body" if hx_request else None


def get_token_from_cookie(token: Annotated[str | None, Cookie()]):
    return AuthHandler().decode_token(token)


def get_user_id_from_token(
    token: Annotated[str | None, Depends(get_token_from_cookie)],
) -> int | None:
    return int(token.get("id"))
