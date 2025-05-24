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
from tests.conftest_helpers import change_to_a_defined_category, remove_id

TEST_CATEGORY_NAME = "древесина"
TEST_PASSWORD = "test_password"
TEST_USER_NAME = "beebo"
TEST_USER_ID = 1
TEST_USER_PASSWORD = "sW0rDf!s4"


@pytest.fixture(scope="function")
def token():
    username = TEST_USER_NAME
    return AuthHandler().encode_token(username=username, id=TEST_USER_ID)


@pytest.fixture(scope="function")
def client(token):
    return TestClient(
        app=build_app(),
        follow_redirects=False,
        cookies={"token": token},
    )


@pytest.fixture(scope="function")
def auth_handler():
    return AuthHandler()


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


def add_user(session) -> User:
    user = User(
        username=TEST_USER_NAME,
        password_hash_sum=hash_password(TEST_USER_PASSWORD),
    )
    session.add(user)
    session.flush()
    session.commit()
    return user


@pytest.fixture(scope="function", autouse=True)
def user(session):
    add_user(session)
    yield
    clean_db(session)


def raise_always(scope="function", *args, **kwargs):
    raise Exception


def clean_db(session):
    session.query(Payment).delete()
    session.query(Category).delete()
    session.query(User).delete()
    session.commit()


def delete_category(session):
    session.query(Category).delete()
    session.commit()


def get_categories(session):
    statement = select(Category)
    res = session.execute(statement)
    return res.scalars().all()


def get_category_by_id(session, category_id: int):
    statement = select(Category).where(Category.id == category_id)
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


def get_user(session):
    statement = select(User)
    res = session.execute(statement)
    return res.scalars().all()[0]


def add_categories(session):
    categories = get_categories(session)
    if not categories:
        for i in range(len(CATEGORIES)):
            category = Category(
                name=CATEGORIES[i], is_active=True, user_id=TEST_USER_ID
            )
            session.flush()
            session.add(category)
        session.commit()


def add_payments(session, user):
    categories = get_categories(session)
    category_ids = [x.id for x in categories]
    for _ in range(10):
        payment = Payment(
            user_id=TEST_USER_ID,
            name=random.choice(PRODUCTS),
            price=random.randrange(100, 5000, 100),
            category_id=random.choice(category_ids),
        )
        session.flush()
        session.add(payment)

    session.commit()


def add_payment(
    session: Session,
    category_id: int,
    created_at: datetime.datetime,
    price: int,
    user,
) -> Payment:
    payment = Payment(
        user_id=TEST_USER_ID,
        name=random.choice(PRODUCTS),
        price=price,
        category_id=category_id,
        created_at=created_at,
    )
    session.flush()
    session.add(payment)
    return payment


@pytest.fixture(scope="function")
def fill_db(session):
    add_categories(session)
    add_payments(session, user)
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


def payment_create_function(payment_as_dict, session, category) -> dict:
    return payment_create_with_id(payment_as_dict, session, category)


@pytest.fixture(scope="function")
def payment_create_no_id(payment_create) -> dict:
    return remove_id(payment_create)


@pytest.fixture(scope="function")
def dict_for_new_payment(payment_create):
    new_dict = copy(payment_create)
    new_dict.pop("id", None)
    new_dict.pop("created_at", None)
    new_dict.pop("updated_at", None)
    new_dict.pop("user_id", None)
    return new_dict


@pytest.fixture(scope="function")
def payment_create_no_category(payment_create_no_id) -> dict:
    new_dict = copy(payment_create_no_id)
    payment_create_no_id.pop("category_id", None)
    return new_dict


@pytest.fixture(scope="function")
def payment_update(payment_as_dict, session, category) -> dict:
    new_dict = payment_create_with_id(payment_as_dict, session, category)
    new_dict["form_disabled"] = True
    new_dict["user_id"] = TEST_USER_ID
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
def category_create(category_as_dict, session) -> dict:
    category = copy(category_as_dict)
    del category["id"]
    del category["created_at"]
    del category["updated_at"]
    del category["is_active"]
    return category


@pytest.fixture(scope="function")
def current_payment(
    category,
    user,
    session: Session,
):
    payment = Payment(
        user_id=TEST_USER_ID,
        name="текущий платёж",
        price=500,
        category_id=category.id,
        created_at=datetime.datetime.now(),
    )
    session.add(payment)
    session.flush()
    return payment


@pytest.fixture(scope="function")
def month_ago_payment(category, user, session: Session):
    payment = Payment(
        user_id=TEST_USER_ID,
        name="платёж прошлого месяца",
        price=500,
        category_id=category.id,
        created_at=datetime.datetime.now() - datetime.timedelta(weeks=8),
    )
    session.add(payment)
    session.flush()
    return payment


@pytest.fixture(scope="function")
def positive_balance(category, user, session: Session):
    payment = Payment(
        user_id=TEST_USER_ID,
        name="зарплата",
        price=500000000,
        category_id=category.id,
        created_at=datetime.datetime.now(),
        is_spending=False,
    )
    session.add(payment)
    session.flush()
    session.commit()
    return payment


@pytest.fixture(scope="function")
def month_ago_payment_later(
    month_ago_payment, category, user, session: Session
):
    payment = Payment(
        user_id=TEST_USER_ID,
        name=random.choice(PRODUCTS),
        price=500,
        category_id=category.id,
        created_at=month_ago_payment.created_at + datetime.timedelta(minutes=3),
    )
    session.add(payment)
    session.flush()
    return payment


@pytest.fixture(scope="function")
def year_ago_payment(category, user, session: Session):
    payment = Payment(
        user_id=TEST_USER_ID,
        name="платёж прошлого года",
        price=500,
        category_id=category.id,
        created_at=datetime.datetime.now() - datetime.timedelta(weeks=53),
    )
    session.add(payment)
    session.flush()
    return payment


@pytest.fixture(scope="function")
def year_after_payment(category, user, session: Session):
    payment = Payment(
        user_id=TEST_USER_ID,
        name=random.choice(PRODUCTS),
        price=500,
        category_id=category.id,
        created_at=datetime.datetime.now() + datetime.timedelta(weeks=53),
    )
    session.add(payment)
    session.flush()
    return payment


@pytest.fixture(scope="function")
def year_ago_payment_later(user, year_ago_payment, category, session: Session):
    payment = Payment(
        user_id=TEST_USER_ID,
        name=random.choice(PRODUCTS),
        price=500,
        category_id=category.id,
        created_at=year_ago_payment.created_at + datetime.timedelta(days=3),
    )
    session.add(payment)
    session.flush()
    return payment


def get_dict_to_create_user(user, session) -> dict:
    user = get_user(session)
    user_dict = dict(
        session.execute(select("*").where(User.id == user.id).select_from(User))
        .mappings()
        .all()[0]
    )
    clean_db(session)
    del user_dict["id"]
    del user_dict["password_hash_sum"]
    user_dict["password"] = TEST_USER_PASSWORD
    return user_dict


@pytest.fixture(scope="function")
def stale_token(auth_handler):
    return auth_handler.encode_token(
        username="test_user",
        id=TEST_USER_ID,
        expires_delta=datetime.timedelta(days=-100),
    )


@pytest.fixture(scope="function")
def wrong_token(auth_handler):
    username = "Poblebonk"
    token = auth_handler.encode_token(username=username, id=TEST_USER_ID)
    return token[10:]


@pytest.fixture(scope="function")
def wrong_user_token(auth_handler):
    username = "Wrong User"
    return auth_handler.encode_token(username=username, id=500)


def check_that_payments_belong_to_test_user(payments: list[Payment]):
    user_ids = set([x.user_id for x in payments])
    assert len(user_ids) == 1
    assert list(user_ids)[0] == TEST_USER_ID
