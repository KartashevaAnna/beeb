from typing import Annotated

from pydantic import (
    BaseModel,
    Field,
    StringConstraints,
    computed_field,
    field_validator,
)

from app.utils.enums import ExpenseCategory
from app.utils.tools.helpers import get_number_for_db, get_readable_price


class ExpenseCreate(BaseModel):
    name: Annotated[
        str,
        StringConstraints(
            min_length=1, max_length=255, strip_whitespace=True, to_lower=True
        ),
    ]
    price: Annotated[int, Field(gt=0)]
    category: ExpenseCategory = Field(default=ExpenseCategory.list_names()[0])

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
    category: ExpenseCategory = Field(default=ExpenseCategory.list_names()[0])

    @computed_field
    @property
    def price_in_rub(cls) -> str:
        return get_readable_price(cls.price)


class ExpenseUpdate(BaseModel):
    name: Annotated[
        str,
        StringConstraints(
            min_length=1, max_length=255, strip_whitespace=True, to_lower=True
        ),
    ]
    price: Annotated[str, Field()]
    category: ExpenseCategory = Field(default=ExpenseCategory.list_names()[0])

    def get_positive_number(self, number) -> int:
        if not number or number <= 0:
            raise ValueError("number must be positive")
        return number

    @computed_field
    @property
    def price_in_kopecks(cls) -> int:
        return cls.get_positive_number(get_number_for_db(cls.price))

    @field_validator("name")
    def prevent_blank_strings(cls, value):
        for _ in range(len(value)):
            value = value.replace("  ", " ")
        assert not value.isspace(), "Empty strings are not allowed."
        return value
