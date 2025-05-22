from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions import (
    DuplicateNameCreateError,
    UserNotFoundError,
    WrongPasswordError,
)
from app.models import User
from app.schemas.users import UserCreate
from app.utils.tools.helpers import is_same_password


class UserRepo:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, user: UserCreate) -> None:
        if self.get_by_username(user.username):
            raise DuplicateNameCreateError(user.username)
        user = User(**user.model_dump())
        self.session.add(user)
        self.session.commit()

    def get_by_username(self, username: str) -> User | None:
        statement = select(User).where(User.username == username)
        result = self.session.execute(statement)
        return result.scalars().one_or_none()

    def login(self, username: str, password: str) -> User:
        user = self.get_by_username(username)
        if not user:
            raise UserNotFoundError(username)
        if not is_same_password(password, user.password_hash_sum):
            raise WrongPasswordError(username=username, password=password)
        return user
