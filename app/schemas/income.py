import datetime
from typing import Annotated
from uuid import UUID
from fastapi import Form
from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    Field,
    StringConstraints,
    computed_field,
    field_validator,
    validator,
)

from app.exceptions import BeebError, EmptyStringError, NotPositiveValueError
from app.utils.tools.helpers import (
    get_date_for_database,
    get_number_for_db,
    get_pure_date_from_datetime,
    get_readable_amount,
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


class IncomeShowOne(IncomeBase):
    created_at: Annotated[datetime.datetime, Field(exclude=True)]
    amount: Annotated[int, Field()]
    user_id: Annotated[int, Field(gt=0, exclude=True)]
    id: Annotated[int, Field(gt=0)]

    @computed_field
    @property
    def date(cls) -> str:
        return get_pure_date_from_datetime(date=cls.created_at)


class IncomeUpdate(BaseModel):
    amount_in_rub: Annotated[
        str,
        Field(exclude=True),
    ]
    frontend_name: Annotated[str, Field(exclude=True)]
    date: Annotated[
        str,
        Field(exclude=True),
    ]

    @computed_field
    @property
    def name(cls) -> str:
        return prevent_blank_strings(cls.frontend_name)

    @computed_field
    @property
    def amount(cls) -> int:
        return validate_positive_number_for_db(
            get_number_for_db(prevent_blank_strings(cls.amount_in_rub))
        )

    @computed_field
    @property
    def created_at(cls) -> datetime.datetime:
        cls.date = prevent_blank_strings(cls.date)
        return get_date_for_database(cls.date)
