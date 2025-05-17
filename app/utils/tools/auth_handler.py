from datetime import datetime, timedelta, timezone

from fastapi import Response
from jose import jwt

from app.settings import SETTINGS


class AuthHandler:
    def __init__(self) -> None:
        self.secret = SETTINGS.secrets.jwt_secret

    def encode_token(
        self,
        email: str,
        expires_delta: timedelta = timedelta(
            seconds=SETTINGS.secrets.session_lifetime
        ),
    ) -> str:
        expires_at = datetime.now(timezone.utc).astimezone() + expires_delta
        payload = {
            "email": email,
            "exp": expires_at,
        }
        return jwt.encode(payload, self.secret)

    def set_cookies(self, response: Response, email: str):
        return response.set_cookie(
            key="token",
            value=self.encode_token(email=email),
            max_age=SETTINGS.secrets.session_lifetime,
            secure=False,
            samesite="lax",
        )
