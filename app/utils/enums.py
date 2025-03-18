from enum import StrEnum


class ExpenseCategory(StrEnum):
    food = "food"
    non_food = "non_food"

    @classmethod
    def list_names(cls):
        return list(map(lambda c: c.name, cls))
