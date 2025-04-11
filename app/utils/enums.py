from enum import StrEnum


class CategoryStatus(StrEnum):
    active = "категория актуальна"
    deprecated = "категория устарела"

    @classmethod
    def list_names(cls):
        return list(map(lambda c: c.name, cls))
