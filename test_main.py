from fastapi.testclient import TestClient

from database import get_db
from main import app


def test_home():
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Inventory API is running"
    }


def test_negative_quantity_rejected():
    def fake_db():
        yield None

    app.dependency_overrides[get_db] = fake_db

    try:
        with TestClient(app) as client:
            response = client.post(
                "/products",
                json={
                    "name": "Test Keyboard",
                    "sku": "TEST-NEGATIVE",
                    "quantity": -5,
                },
            )

        assert response.status_code == 422

        errors = response.json()["detail"]

        assert any(
            error["loc"] == ["body", "quantity"]
            and error["type"] == "greater_than_equal"
            for error in errors
        )
    finally:
        del app.dependency_overrides[get_db]