from uuid import uuid4


def test_product_lifecycle(client):
    product_data = {
        "name": "Test Keyboard",
        "sku": f"TEST-{uuid4().hex}",
        "quantity": 10,
    }

    # Create
    response = client.post("/products", json=product_data)

    assert response.status_code == 201
    created = response.json()
    product_id = created["id"]

    assert created["name"] == "Test Keyboard"
    assert created["quantity"] == 10

    # Read
    response = client.get(f"/products/{product_id}")

    assert response.status_code == 200
    assert response.json() == created

    # Update
    updated_data = {**product_data, "quantity": 25}
    response = client.put(
        f"/products/{product_id}",
        json=updated_data,
    )

    assert response.status_code == 200
    assert response.json()["quantity"] == 25

    # Verify the update through a new request
    response = client.get(f"/products/{product_id}")

    assert response.status_code == 200
    assert response.json()["quantity"] == 25

    # Delete
    response = client.delete(f"/products/{product_id}")

    assert response.status_code == 200

    # Verify it no longer exists
    response = client.get(f"/products/{product_id}")

    assert response.status_code == 404

def test_duplicate_sku_rejected(client):
    product_data = {
        "name": "Original Keyboard",
        "sku": f"TEST-{uuid4().hex}",
        "quantity": 10,
    }

    first_response = client.post(
        "/products",
        json=product_data,
    )
    assert first_response.status_code == 201

    duplicate_data = {
        **product_data,
        "name": "Duplicate Keyboard",
    }

    second_response = client.post(
        "/products",
        json=duplicate_data,
    )

    assert second_response.status_code == 409
    assert second_response.json()["detail"] == (
        "A product with this SKU already exists"
    )

    product_id = first_response.json()["id"]
    saved_response = client.get(f"/products/{product_id}")

    assert saved_response.status_code == 200
    assert saved_response.json()["name"] == "Original Keyboard"