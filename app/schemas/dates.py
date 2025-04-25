from pydantic import BaseModel, Field


class DateFilter(BaseModel):
    year: int | None = Field(default=None)
    month: int | None = Field(default=None)
