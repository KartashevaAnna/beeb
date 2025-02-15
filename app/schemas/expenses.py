from typing import Annotated

from pydantic import (
    BaseModel,
    Field,
    StringConstraints,
    computed_field,
    field_validator,
)

from app.utils.tools.helpers import get_readable_price


class ExpenseCreate(BaseModel):
    name: Annotated[
        str,
        StringConstraints(
            min_length=1, max_length=255, strip_whitespace=True, to_lower=True
        ),
    ]
    price: Annotated[int, Field(gt=0)]

    @field_validator("name")
    def prevent_blank_strings(cls, value):
        for _ in range(len(value)):
            value = value.replace("  ", " ")
        assert not value.isspace(), "Empty strings are not allowed."
        return value


class ExpenseShow(BaseModel):
    id: Annotated[int, Field]
    name: Annotated[str, Field()]
    price: Annotated[int, Field()]

    @computed_field
    @property
    def price_in_rub(cls) -> str:
        return get_readable_price(cls.price)
