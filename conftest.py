import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database import database_url, get_db
from main import app
from models import Base


@pytest.fixture
def client():
    test_db_name = os.getenv("TEST_DB_NAME")

    if (
        test_db_name != "inventory_test_db"
        or test_db_name == database_url.database
    ):
        raise RuntimeError("Tests must use inventory_test_db")

    test_url = database_url.set(database=test_db_name)
    test_engine = create_engine(test_url, pool_pre_ping=True)

    try:
        Base.metadata.create_all(test_engine)

        with test_engine.connect() as connection:
            transaction = connection.begin()

            try:
                with Session(
                    bind=connection,
                    join_transaction_mode="create_savepoint",
                ) as session:

                    def override_get_db():
                        yield session

                    app.dependency_overrides[get_db] = override_get_db

                    try:
                        with TestClient(app) as test_client:
                            yield test_client
                    finally:
                        del app.dependency_overrides[get_db]
            finally:
                transaction.rollback()
    finally:
        test_engine.dispose()