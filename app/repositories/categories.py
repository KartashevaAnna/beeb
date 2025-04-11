from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models import Category
from app.schemas.categories import CategoryCreate, CategoryShowOne
from app.utils.enums import CategoryStatus
from app.utils.tools.helpers import sort_options


class CategoryRepo:
    def __init__(self, session: Session) -> None:
        self.session = session

    def read_all(self) -> list[Category]:
        statement = select(Category)
        res = self.session.execute(statement)
        return res.scalars().all()

    def list_names(self) -> list[str]:
        results = self.read_all()
        return [x.name for x in results]

    def list_statuses(self) -> list[str]:
        return CategoryStatus.list_names()

    def get_dict_names(self) -> dict:
        statement = select(Category)
        res = self.session.execute(statement)
        res = res.scalars().all()
        tmp_list = [dict(sub.__dict__.items()) for sub in res]
        all_keys = [x["name"] for x in tmp_list]
        all_values = [x["id"] for x in tmp_list]
        return dict(zip(all_keys, all_values))

    def get_expenses_options(self, current_option: str | None = None) -> list:
        """Gets all expenses options.

        Sorts options so that:
        - the one currently selected is on top
        - if nothing is selected, first created category shall always be on top"
        """
        all_options = self.list_names()
        return sort_options(all_options, current_option)

    def get_status_options(self, current_option: str | None = None) -> list:
        """Gets all status options.

        Sorts options so that:
        - the one currently selected is on top
        - if nothing is selected, first created status shall always be on top"
        """
        all_options = self.list_statuses()
        return sort_options(all_options, current_option)

    def read_name(self, category_name: str) -> Category | None:
        statement = select(Category).where(Category.name == category_name)
        results = self.session.execute(statement)
        category = results.scalars().all()
        return (
            CategoryShowOne(
                **category[0].__dict__,
            )
            if category
            else None
        )

    def read(self, category_id: int) -> Category | None:
        statement = select(Category).where(Category.id == category_id)
        results = self.session.execute(statement)
        category = results.scalars().all()
        return (
            CategoryShowOne(
                **category[0].__dict__,
            )
            if category
            else None
        )

    def create(self, category: CategoryCreate) -> Category:
        new_category = Category(**category.model_dump())
        self.session.add(new_category)
        self.session.commit()
        statement = select(Category).where(Category.id == new_category.id)
        results = self.session.execute(statement)
        return results.scalars().one_or_none()

    def update(self, category_id: int, to_update: CategoryCreate):
        stmt = (
            update(Category)
            .where(Category.id == category_id)
            .values(name=to_update.name, status=to_update.status)
        )
        self.session.execute(stmt)
        self.session.commit()
