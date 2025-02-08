from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints, field_validator


class ExpenseCreate(BaseModel):
    name: Annotated[str, StringConstraints(min_length=1, max_length=255, strip_whitespace=True, to_lower=True)]
    price: Annotated[int, Field(gt=0)]

    @field_validator("name")
    def prevent_blank_strings(cls, value):
        for _ in range(len(value)):
            value = value.replace("  ", " ")
        assert not value.isspace(), "Empty strings are not allowed."
        return value
