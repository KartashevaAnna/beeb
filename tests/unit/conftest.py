import random
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import functions

from app.application import build_app
from app.models import AlchemyBaseModel, Expense
from app.settings import ENGINE
from app.utils.enums import ExpenseCategory
from tests.constants import PRODUCTS


@pytest.fixture(scope="session")
def client():
    return TestClient(app=build_app(), follow_redirects=False)


@pytest.fixture(scope="session")
def session():
    engine = ENGINE
    sa_session = sessionmaker(bind=engine)
    with sa_session() as session:
        yield session
    AlchemyBaseModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def migrate(session):
    migrations_dir = Path("./migrations")
    migrations_list = list(migrations_dir.iterdir())
    for migration in sorted(migrations_list):
        with open(file=migration, mode="r") as migration_file:
            with session.begin():
                session.execute(text(migration_file.read()))


def raise_always(scope="function", *args, **kwargs):
    raise Exception


def clean_db(session):
    session.query(Expense).delete()
    session.commit()


def add_expenses(session):
    for _ in range(10):
        expense = Expense(
            name=random.choice(PRODUCTS),
            price=random.randrange(100, 5000, 100),
            category=random.choice(ExpenseCategory.list_names()),
        )
        session.add(expense)
        session.flush()
    session.commit()


@pytest.fixture(scope="function")
def fill_db(session):
    add_expenses(session)
    yield
    clean_db(session)


@pytest.fixture(scope="function")
def total_expenses(session):
    statement = select(functions.sum(Expense.price))
    results = session.execute(statement)
    return results.scalars().first()
