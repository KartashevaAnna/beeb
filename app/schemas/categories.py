from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints, field_validator

from app.utils.enums import CategoryStatus


class CategoryCreate(BaseModel):
    name: Annotated[
        str,
        StringConstraints(
            min_length=1, max_length=255, strip_whitespace=True, to_lower=True
        ),
    ]
    status: CategoryStatus = Field(default=CategoryStatus.active)

    @field_validator("name")
    def prevent_blank_strings(cls, value):
        for _ in range(len(value)):
            value = value.replace("  ", " ")
        assert not value.isspace(), "Empty strings are not allowed."
        return value


class CategoryShowOne(BaseModel):
    id: Annotated[int, Field()]
    name: Annotated[str, Field()]
    status: Annotated[str, Field()]
