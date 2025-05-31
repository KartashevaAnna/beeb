import datetime
from typing import Annotated
from pydantic import (
    BaseModel,
    Field,
    StringConstraints,
    computed_field,
    field_validator,
)

from app.exceptions import BeebError
from app.utils.tools.helpers import (
    prevent_blank_strings,
    validate_positive_number_for_db,
)


class IncomeBase(BaseModel):
    name: Annotated[
        str,
        StringConstraints(
            min_length=1, max_length=255, strip_whitespace=True, to_lower=True
        ),
    ]


class IncomeCreate(IncomeBase):
    amount_in_rub: Annotated[int, Field(exclude=True)]
    created_at: datetime.datetime
    user_id: Annotated[int, Field(gt=0)]

    @field_validator("amount_in_rub", mode="before")
    @classmethod
    def validate_amount_in_rub(cls, value) -> int | BeebError:
        return validate_positive_number_for_db(value)

    @computed_field
    @property
    def amount(cls) -> str:
        return f"{cls.amount_in_rub}00"

    @field_validator("name")
    def prevent_blank_name(cls, value):
        return prevent_blank_strings(value)
