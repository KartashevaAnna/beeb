import datetime
from typing import Annotated

from pydantic import (
    BaseModel,
    Field,
    StringConstraints,
    computed_field,
    field_validator,
)

from app.utils.tools.helpers import (
    get_date_from_datetime,
    get_datetime_from_date,
    get_number_for_db,
    get_readable_price,
)


class PaymentShow(BaseModel):
    id: Annotated[int, Field()]
    name: Annotated[str, Field()]
    price: Annotated[int, Field()]
    category: Annotated[str, Field()]
    created_at: Annotated[datetime.datetime, Field(exclude=True)]

    @computed_field
    @property
    def price_in_rub(cls) -> str:
        return get_readable_price(cls.price)

    @computed_field
    @property
    def date(cls) -> str:
        return get_date_from_datetime(date=cls.created_at)


class PaymentShowOne(PaymentShow):
    category: Annotated[str, Field()]


class PaymentCreate(BaseModel):
    name: Annotated[
        str,
        StringConstraints(
            min_length=1, max_length=255, strip_whitespace=True, to_lower=True
        ),
    ]
    price: Annotated[int, Field(gt=0)]
    category_id: int = Field()

    @field_validator("name")
    def prevent_blank_strings(cls, value):
        for _ in range(len(value)):
            value = value.replace("  ", " ")
        assert not value.isspace(), "Empty strings are not allowed."
        return value


class PaymentUpdate(PaymentCreate):
    price: Annotated[str, Field()]
    date: Annotated[
        str,
        StringConstraints(
            min_length=1, max_length=255, strip_whitespace=True, to_lower=True
        ),
    ]

    def get_positive_number(self, number) -> int:
        if not number or number <= 0:
            raise ValueError("number must be positive")
        return number

    @field_validator("date")
    def prevent_blank_strings(cls, value):
        for _ in range(len(value)):
            value = value.replace("  ", " ")
        assert not value.isspace(), "Empty strings are not allowed."
        return value

    @computed_field
    @property
    def price_in_kopecks(cls) -> int:
        return cls.get_positive_number(get_number_for_db(cls.price))

    @computed_field
    @property
    def date_to_update(cls) -> datetime.datetime:
        return get_datetime_from_date(cls.date)
