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

def test_blank_product_name_rejected(client):
    response = client.post(
        "/products",
        json={
            "name": "   ",
            "sku": f"TEST-{uuid4().hex}",
            "quantity": 10,
        },
    )

    assert response.status_code == 422

    errors = response.json()["detail"]

    assert any(
        error["loc"] == ["body", "name"]
        and error["type"] == "string_too_short"
        for error in errors
    )

def test_search_and_pagination(client):
    unique_text = uuid4().hex

    for number in range(3):
        response = client.post(
            "/products",
            json={
                "name": f"Keyboard {unique_text} {number}",
                "sku": f"{unique_text}-{number}",
                "quantity": 10,
            },
        )
        assert response.status_code == 201

    first_response = client.get(
        "/products",
        params={
            "search": unique_text,
            "offset": 0,
            "limit": 2,
        },
    )

    assert first_response.status_code == 200
    first_page = first_response.json()

    assert len(first_page) == 2
    assert first_page[0]["name"] == f"Keyboard {unique_text} 0"
    assert first_page[1]["name"] == f"Keyboard {unique_text} 1"

    second_response = client.get(
        "/products",
        params={
            "search": unique_text,
            "offset": 2,
            "limit": 2,
        },
    )

    assert second_response.status_code == 200
    second_page = second_response.json()

    assert len(second_page) == 1
    assert second_page[0]["name"] == f"Keyboard {unique_text} 2"

    no_match_response = client.get(
        "/products",
        params={"search": f"missing-{unique_text}"},
    )

    assert no_match_response.status_code == 200
    assert no_match_response.json() == []