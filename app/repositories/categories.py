from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Category


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
        first_option = all_options[0]
        all_options.remove(first_option)
        if current_option not in all_options:
            sorted_options = []
        else:
            sorted_options = [current_option]
            all_options.remove(current_option)
        all_options = sorted(all_options)
        sorted_options.append((first_option))
        sorted_options.extend(iter(all_options))
        return sorted_options
