from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions import DuplicateEmailError
from app.models import User
from app.utils.tools.helpers import hash_password


class UserRepo:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        email: EmailStr,
        password: str,
        first_name: str,
        last_name: str,
    ) -> None:
        if self.get_by_email(email):
            raise DuplicateEmailError(email)
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash_sum=hash_password(password),
        )
        self.session.add(user)
        self.session.commit()

    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        result = self.session.execute(statement)
        return result.scalars().one_or_none()
