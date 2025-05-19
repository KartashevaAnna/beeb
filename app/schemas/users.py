from pydantic import BaseModel, Field, computed_field, field_validator

from app.utils.tools.helpers import hash_password, prevent_blank_strings


class UserCreate(BaseModel):
    username: str = Field(
        max_length=255,
        json_schema_extra={"strip_whitespace": True},
    )
    password: str = Field(
        max_length=255,
        exclude=True,
        json_schema_extra={"strip_whitespace": True},
    )

    @field_validator("username")
    def prevent_blank_username(cls, value):
        return prevent_blank_strings(value)

    @field_validator("password")
    def prevent_blank_password(cls, value):
        return prevent_blank_strings(value)

    @computed_field
    @property
    def password_hash_sum(cls) -> bytes:
        return hash_password(cls.password)
