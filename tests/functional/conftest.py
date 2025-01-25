import pytest
from fastapi.testclient import TestClient

from app.application import build_app


@pytest.fixture(scope="function")
def client():
    return TestClient(app=build_app(), follow_redirects=False)
