from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.exceptions import (DuplicateNameCreateError, DuplicateNameEditError,
                            NotOwnerError)
from app.models import Category
from app.schemas.categories import CategoryCreate, CategoryShowOne
from app.utils.tools.helpers import sort_options


class CategoryRepo:
    def __init__(self, session: Session) -> None:
        self.session = session

    def read_all(self, user_id: int) -> list[Category]:
        statement = (
            select(Category)
            .where(Category.user_id == user_id)
            .order_by(Category.name)
        )
        res = self.session.execute(statement)
        return res.scalars().all()

    def list_names(self, user_id: int) -> list[str]:
        results = self.read_all(user_id)
        return [x.name for x in results]

    def list_statuses(self) -> list[str]:
        return [True, False]

    def get_dict_names(self, user_id: int) -> dict:
        statement = select(Category).where(Category.user_id == user_id)
        res = self.session.execute(statement)
        res = res.scalars().all()
        tmp_list = [dict(sub.__dict__.items()) for sub in res]
        all_keys = [x["name"] for x in tmp_list]
        all_values = [x["id"] for x in tmp_list]
        return dict(zip(all_keys, all_values))

    def get_payments_options(
        self,
        user_id: int,
        current_option: str | None = None,
    ) -> list:
        """Gets all payments options.

        Sorts options so that:
        - the one currently selected is on top
        - if nothing is selected, first created category shall always be on top"
        """
        all_options = self.list_names(user_id)
        return sort_options(all_options, current_option)

    def get_status_options(self, current_option: str | None = None) -> list:
        """Gets all status options.

        Sorts options so that:
        - the one currently selected is on top
        - if nothing is selected, first created status shall always be on top"
        """
        all_options = self.list_statuses()
        return sort_options(all_options, current_option)

    def read_name(self, category_name: str, user_id: int) -> Category | None:
        statement = select(Category).where(
            (Category.name == category_name) & (Category.user_id == user_id)
        )
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

    def create(
        self,
        category: CategoryCreate,
    ) -> Category:
        if new_category := self.read_name(
            category_name=category.name, user_id=category.user_id
        ):
            raise DuplicateNameCreateError(category.name)
        new_category = Category(**category.model_dump())
        self.session.add(new_category)
        self.session.commit()
        statement = select(Category).where(Category.id == new_category.id)
        results = self.session.execute(statement)
        return results.scalars().one_or_none()

    def update(self, category_id: int, to_update: CategoryCreate):
        previous_state = self.read(category_id)
        if previous_state.user_id != to_update.user_id:
            raise NotOwnerError(previous_state.name)
        category_with_the_same_name = self.read_name(
            to_update.name, user_id=to_update.user_id
        )
        if category_with_the_same_name:
            if category_with_the_same_name.id != category_id:
                raise DuplicateNameEditError(category_with_the_same_name.name)
        stmt = (
            update(Category)
            .where(Category.id == category_id)
            .values(name=to_update.name, is_active=to_update.is_active)
        )
        self.session.execute(stmt)
        self.session.commit()
