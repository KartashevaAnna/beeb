from pydantic import BaseModel, conint


class ExpenseCreate(BaseModel):
    name: str
    calories: int = conint(gt=0)
    price: int = conint(gt=0)
