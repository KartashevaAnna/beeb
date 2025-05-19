from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints, field_validator

from app.utils.tools.helpers import prevent_blank_strings


class CategoryCreate(BaseModel):
    name: Annotated[
        str,
        StringConstraints(
            min_length=1, max_length=255, strip_whitespace=True, to_lower=True
        ),
    ]
    is_active: Annotated[bool, Field(default=True)]

    @field_validator("name")
    def prevent_blank_strings(cls, value):
        return prevent_blank_strings(value)


class CategoryShowOne(BaseModel):
    id: Annotated[int, Field()]
    name: Annotated[str, Field()]
    is_active: Annotated[bool, Field()]
