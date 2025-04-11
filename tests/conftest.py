import datetime
import random
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql import functions

from app.application import build_app
from app.models import AlchemyBaseModel, Category, Expense
from app.settings import ENGINE
from app.utils.constants import CATEGORIES, PRODUCTS
from app.utils.enums import CategoryStatus


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
    session.query(Category).delete()
    session.commit()


def get_categories(session):
    statement = select(Category)
    res = session.execute(statement)
    return res.scalars().all()


def get_expenses(session):
    statement = select(Expense)
    res = session.execute(statement)
    return res.scalars().all()


def add_categories(session):
    categories = get_categories(session)
    if not categories:
        for i in range(len(CATEGORIES)):
            category = Category(
                name=CATEGORIES[i], status=CategoryStatus.active.value
            )
            session.add(category)
            session.flush()
        session.commit()


def add_expenses(session):
    categories = get_categories(session)
    category_ids = [x.id for x in categories]
    for _ in range(10):
        expense = Expense(
            name=random.choice(PRODUCTS),
            price=random.randrange(100, 5000, 100),
            category_id=random.choice(category_ids),
        )
        session.add(expense)
        session.flush()
    session.commit()


def add_expense(
    session: Session,
    category_id: int,
    created_at: datetime.datetime,
    price: int,
) -> Expense:
    expense = Expense(
        name=random.choice(PRODUCTS),
        price=price,
        category_id=category_id,
        created_at=created_at,
    )
    session.add(expense)
    session.flush()
    return expense


@pytest.fixture(scope="function")
def fill_db(session):
    add_categories(session)
    add_expenses(session)
    yield
    clean_db(session)


@pytest.fixture(scope="function")
def categories(session):
    add_categories(session)
    yield
    clean_db(session)


@pytest.fixture(scope="function")
def category(categories, session):
    statement = select(Category)
    res = session.execute(statement)
    return res.scalars().all()[0]


@pytest.fixture(scope="function")
def expense(fill_db, session):
    return session.scalars(select(Expense).join(Category)).all()[0]


@pytest.fixture(scope="function")
def total_expenses(session):
    statement = select(functions.sum(Expense.price))
    results = session.execute(statement)
    return results.scalars().first()
