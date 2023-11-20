import pytest
from typing import Generator, Any
from fastapi.testclient import TestClient
from fastapi import FastAPI
from ..main import app
from .. import database
import secrets
from pymongo.database import Database


# https://www.fastapitutorial.com/blog/unit-testing-in-fastapi/
# https://fastapi.tiangolo.com/advanced/testing-database/


@pytest.fixture(scope="function")
def test_db() -> Generator[Database, Any, None]:
    """
    Return a temporary database that is automatically removed when the test function terminates
    """
    #test db creation
    test_db_name = "pytest-" + secrets.token_hex(16)
    test_db = database.client[test_db_name]
    yield test_db
    #test db cleanup
    database.client.drop_database(test_db_name)


@pytest.fixture(scope="function")
def client(
    test_db: Database
) -> Generator[TestClient, Any, None]:
    """
    Create a new FastAPI TestClient that uses the `test_db` fixture to override
    the `get_db` dependency that is injected into routes.
    """

    def _get_test_db():
        """ Return a test version of the MongoDb Scanner database
        """
        return test_db

    app.dependency_overrides[database.get_db] = _get_test_db
    with TestClient(app) as client:
        yield client