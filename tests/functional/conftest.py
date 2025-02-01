from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from app.application import build_app
from app.models import AlchemyBaseModel, Expense
from app.settings import ENGINE


@pytest.fixture(scope="function")
def client():
    return TestClient(app=build_app(), follow_redirects=False)


@pytest.fixture(scope="function")
def session():
    engine = ENGINE
    sa_session = sessionmaker(autocommit=False, bind=engine, expire_on_commit=True)
    with sa_session() as session:
        yield session
    AlchemyBaseModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function", autouse=True)
def execute_migrations(session):
    migrations_dir = Path("./migrations")
    migrations_list = list(migrations_dir.iterdir())
    for migration in sorted(migrations_list):
        with open(file=migration, mode="r", encoding="utf-8") as migration_file:
            session.execute(text(migration_file.read()))
        session.commit()


def raise_always(scope="function", *args, **kwargs):
    raise Exception


@pytest.fixture(scope="function")
def add_expenses(client) -> Expense:
    client.post("/create-expenses-in-db")
