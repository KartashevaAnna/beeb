import datetime
from typing import Annotated
from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
    StringConstraints,
    computed_field,
    field_validator,
)

from app.exceptions import (
    NotIntegerError,
    NotPositiveValueError,
    ValueTooLargeError,
)
from app.utils.tools.helpers import (
    get_date_for_database,
    get_date_from_datetime_without_year,
    get_number_for_db,
    get_pure_date_from_datetime,
    get_readable_amount,
    get_readable_number,
    prevent_blank_strings,
    validate_positive_number_for_db,
)


class PaymentBase(BaseModel):
    name: Annotated[
        str,
        StringConstraints(
            min_length=1, max_length=255, strip_whitespace=True, to_lower=True
        ),
    ]
    category_id: int = Field()
    grams: Annotated[int, Field(gt=0)] | None = None
    quantity: Annotated[int, Field(gt=0)] | None = None


class PaymentShow(PaymentBase):
    id: Annotated[int, Field()]
    uuid: UUID
    amount: Annotated[int, Field()]
    created_at: Annotated[datetime.datetime, Field(exclude=True)]
    category: str | None = None
    category_id: int | None = None
    user_id: Annotated[int, Field(exclude=True)]

    @computed_field
    @property
    def readable_grams(cls) -> str:
        return get_readable_number(cls.grams) if cls.grams else None

    @computed_field
    @property
    def readable_quantity(cls) -> str:
        return get_readable_number(cls.quantity) if cls.quantity else None

    @computed_field
    @property
    def amount_in_rub(cls) -> str:
        return get_readable_amount(cls.amount) if cls.amount else None

    @computed_field
    @property
    def date(cls) -> str:
        return get_date_from_datetime_without_year(date=cls.created_at)

    @computed_field
    @property
    def type(cls) -> str:
        if not any([cls.grams, cls.quantity, cls.category_id]):
            return "доход"
        elif not cls.quantity:
            return "еда"
        return "вещь"

    @field_validator("category", mode="before")
    @classmethod
    def validate_category(cls, value) -> str:
        if not value:
            return "зарплата"
        return value


class PaymentShowOne(PaymentShow):
    user_id: Annotated[int, Field(gt=0, exclude=True)]

    @computed_field
    @property
    def date(cls) -> str:
        return get_pure_date_from_datetime(date=cls.created_at)


class PaymentCreate(PaymentBase):
    amount_in_rub: Annotated[int, Field(exclude=True)]
    created_at: datetime.datetime
    user_id: Annotated[int, Field(gt=0)]

    @field_validator("amount_in_rub", mode="before")
    @classmethod
    def validate_amount_in_rub(cls, value) -> int:
        return validate_positive_number_for_db(value)

    @field_validator("grams", mode="before")
    @classmethod
    def validate_grams(cls, value) -> int | None:
        return validate_positive_number_for_db(value)

    @field_validator("quantity", mode="before")
    @classmethod
    def validate_quantity(cls, value) -> int | None:
        return validate_positive_number_for_db(value)

    @computed_field
    @property
    def amount(cls) -> str:
        return f"{cls.amount_in_rub}00"

    @field_validator("name")
    def prevent_blank_name(cls, value):
        return prevent_blank_strings(value)


class PaymentUpdate(PaymentBase):
    amount: Annotated[str, Field()]
    date: Annotated[
        str,
        StringConstraints(
            min_length=1, max_length=255, strip_whitespace=True, to_lower=True
        ),
        Field(exclude=True),
    ]
    user_id: Annotated[int, Field(gt=0, exclude=True)]

    @field_validator("date")
    def prevent_blank_strings(cls, value):
        return prevent_blank_strings(value)

    @field_validator("amount")
    def prevent_blank_strings(cls, value):
        return prevent_blank_strings(value)

    @computed_field
    @property
    def amount_in_kopecks(cls) -> int:
        return validate_positive_number_for_db(get_number_for_db(cls.amount))

    @computed_field
    @property
    def date_to_update(cls) -> datetime.datetime:
        return get_date_for_database(cls.date)
