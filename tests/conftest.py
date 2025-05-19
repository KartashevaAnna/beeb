import datetime
import random
from copy import copy
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql import functions

from app.application import build_app
from app.models import AlchemyBaseModel, Category, Payment, User
from app.settings import ENGINE
from app.utils.constants import CATEGORIES, PRODUCTS
from app.utils.tools.auth_handler import AuthHandler
from app.utils.tools.helpers import get_date_from_datetime, hash_password
from tests.conftest_helpers import (
    change_to_a_defined_category,
    get_test_user_dict,
    remove_id,
)

TEST_CATEGORY_NAME = "древесина"
TEST_PASSWORD = "test_password"


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
    session.query(Payment).delete()
    session.query(Category).delete()
    session.query(User).delete()
    session.commit()


def get_categories(session):
    statement = select(Category)
    res = session.execute(statement)
    return res.scalars().all()


def get_payments(session):
    statement = select(Payment)
    res = session.execute(statement)
    return res.scalars().all()


def get_users(session):
    statement = select(User)
    res = session.execute(statement)
    return res.scalars().all()


def add_categories(session):
    categories = get_categories(session)
    if not categories:
        for i in range(len(CATEGORIES)):
            category = Category(name=CATEGORIES[i], is_active=True)
            session.add(category)
            session.flush()
        session.commit()


def add_payments(session):
    categories = get_categories(session)
    category_ids = [x.id for x in categories]
    for _ in range(10):
        payment = Payment(
            name=random.choice(PRODUCTS),
            price=random.randrange(100, 5000, 100),
            category_id=random.choice(category_ids),
        )
        session.add(payment)
        session.flush()
    session.commit()


def add_payment(
    session: Session,
    category_id: int,
    created_at: datetime.datetime,
    price: int,
) -> Payment:
    payment = Payment(
        name=random.choice(PRODUCTS),
        price=price,
        category_id=category_id,
        created_at=created_at,
    )
    session.add(payment)
    session.flush()
    return payment


@pytest.fixture(scope="function")
def fill_db(session):
    add_categories(session)
    add_payments(session)
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
def payment(fill_db, session):
    return session.scalars(select(Payment).join(Category)).all()[0]


@pytest.fixture(scope="function")
def total_payments(session):
    statement = select(functions.sum(Payment.price))
    results = session.execute(statement)
    return results.scalars().first()


@pytest.fixture(scope="function")
def payment_as_dict(payment, session) -> dict:
    return dict(
        session.execute(
            select("*").where(Payment.id == payment.id).select_from(Payment)
        )
        .mappings()
        .all()[0]
    )


def add_category_name(payment_as_dict, session):
    new_dict = payment_as_dict
    statement = select(Category).where(
        Category.id == new_dict.get("category_id")
    )
    result = session.execute(statement)
    category = result.scalars().first()
    new_dict["category"] = category.name
    return new_dict


def change_created_at_to_date(payment_as_dict):
    new_dict = copy(payment_as_dict)
    date = new_dict.pop("created_at", None)
    new_dict["date"] = get_date_from_datetime(date)
    return new_dict


def payment_create_with_id(payment_as_dict, session, category) -> dict:
    new_dict = copy(payment_as_dict)
    new_dict = change_to_a_defined_category(payment_as_dict, category)
    new_dict = add_category_name(payment_as_dict, session)
    new_dict = change_created_at_to_date(new_dict)
    return new_dict


@pytest.fixture(scope="function")
def payment_create(payment_as_dict, session, category) -> dict:
    return payment_create_with_id(payment_as_dict, session, category)


@pytest.fixture(scope="function")
def payment_create_no_id(payment_create) -> dict:
    return remove_id(payment_create)


@pytest.fixture(scope="function")
def payment_create_no_category(payment_create_no_id) -> dict:
    new_dict = copy(payment_create_no_id)
    payment_create_no_id.pop("category_id", None)
    return new_dict


@pytest.fixture(scope="function")
def payment_update(payment_as_dict, session, category) -> dict:
    new_dict = payment_create_with_id(payment_as_dict, session, category)
    new_dict["form_disabled"] = True
    return new_dict


def get_newly_created_payment(max_id_before: int, session: Session) -> Payment:
    statement = select(Payment).where(Payment.id == (max_id_before + 1))
    results = session.execute(statement)
    return results.scalars().one_or_none()


@pytest.fixture(scope="function")
def category_as_dict(category, session) -> dict:
    return dict(
        session.execute(
            select("*").where(Category.id == category.id).select_from(Category)
        )
        .mappings()
        .all()[0]
    )


@pytest.fixture(scope="function")
def category_create() -> dict:
    return {"name": TEST_CATEGORY_NAME}


@pytest.fixture(scope="function")
def current_payment(category, session: Session):
    payment = Payment(
        name=random.choice(PRODUCTS),
        price=500,
        category_id=category.id,
        created_at=datetime.datetime.now(),
    )
    session.add(payment)
    session.flush()
    return payment


@pytest.fixture(scope="function")
def month_ago_payment(category, session: Session):
    payment = Payment(
        name=random.choice(PRODUCTS),
        price=500,
        category_id=category.id,
        created_at=datetime.datetime.now() - datetime.timedelta(weeks=8),
    )
    session.add(payment)
    session.flush()
    return payment


@pytest.fixture(scope="function")
def month_ago_payment_later(month_ago_payment, category, session: Session):
    payment = Payment(
        name=random.choice(PRODUCTS),
        price=500,
        category_id=category.id,
        created_at=month_ago_payment.created_at + datetime.timedelta(days=3),
    )
    session.add(payment)
    session.flush()
    return payment


@pytest.fixture(scope="function")
def year_ago_payment(category, session: Session):
    payment = Payment(
        name=random.choice(PRODUCTS),
        price=500,
        category_id=category.id,
        created_at=datetime.datetime.now() - datetime.timedelta(weeks=53),
    )
    session.add(payment)
    session.flush()
    return payment


@pytest.fixture(scope="function")
def year_after_payment(category, session: Session):
    payment = Payment(
        name=random.choice(PRODUCTS),
        price=500,
        category_id=category.id,
        created_at=datetime.datetime.now() + datetime.timedelta(weeks=53),
    )
    session.add(payment)
    session.flush()
    return payment


@pytest.fixture(scope="function")
def year_ago_payment_later(year_ago_payment, category, session: Session):
    payment = Payment(
        name=random.choice(PRODUCTS),
        price=500,
        category_id=category.id,
        created_at=year_ago_payment.created_at + datetime.timedelta(days=3),
    )
    session.add(payment)
    session.flush()
    return payment


@pytest.fixture(scope="function")
def user(session: Session):
    user_dict = get_test_user_dict()
    user_dict["password_hash_sum"] = hash_password(user_dict["password"])
    del user_dict["password"]
    user = User(**user_dict)
    session.add(user)
    session.flush()
    return user


@pytest.fixture(scope="function")
def auth_handler():
    return AuthHandler()


@pytest.fixture(scope="function")
def token(auth_handler):
    username = "test_username"
    email = "test_email"
    return auth_handler.encode_token(username, email)
