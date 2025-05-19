import datetime
from datetime import timedelta

from fastapi import Response
from jose import ExpiredSignatureError, JWTError, jwt

from app.exceptions import ExpiredTokenError, InvalidTokenError
from app.settings import SETTINGS


class AuthHandler:
    def __init__(self) -> None:
        self.secret = SETTINGS.secrets.jwt_secret

    def encode_token(
        self,
        username: str,
        id: int,
        expires_delta: timedelta = timedelta(
            seconds=SETTINGS.secrets.session_lifetime
        ),
    ) -> str:
        expires_at = datetime.datetime.now(datetime.UTC) + expires_delta

        payload = {
            "username": username,
            "id": id,
            "exp": expires_at,
        }
        return jwt.encode(payload, self.secret)

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, self.secret)
        except ExpiredSignatureError as exc:
            raise ExpiredTokenError from exc
        except JWTError as exc:
            raise InvalidTokenError from exc

    def set_cookies(self, response: Response, username: str, id: int):
        return response.set_cookie(
            key="token",
            value=self.encode_token(username=username, id=id),
            max_age=SETTINGS.secrets.session_lifetime,
            secure=False,
            samesite="lax",
        )
