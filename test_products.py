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

    # Update the product name
    updated_data = {
        **product_data,
        "name": "Updated Test Keyboard",
    }

    response = client.put(
        f"/products/{product_id}",
        json=updated_data,
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Test Keyboard"
    assert response.json()["quantity"] == 10

    # Verify the saved update through GET
    response = client.get(f"/products/{product_id}")

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Test Keyboard"
    assert response.json()["quantity"] == 10

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

def test_stock_movements(client):
    response = client.post(
        "/products",
        json={
            "name": "Stock Test Keyboard",
            "sku": f"TEST-{uuid4().hex}",
            "quantity": 10,
        },
    )
    assert response.status_code == 201
    product_id = response.json()["id"]

    movement_url = f"/products/{product_id}/stock-movements"

    # Receive five units: 10 + 5 = 15
    response = client.post(
        movement_url,
        json={
            "quantity_change": 5,
            "reason": "Supplier delivery",
        },
    )
    assert response.status_code == 201
    assert response.json()["quantity"] == 15

    # Sell three units: 15 - 3 = 12
    response = client.post(
        movement_url,
        json={
            "quantity_change": -3,
            "reason": "Customer sale",
        },
    )
    assert response.status_code == 201
    assert response.json()["quantity"] == 12

    # Reject a sale larger than the available stock
    response = client.post(
        movement_url,
        json={
            "quantity_change": -20,
            "reason": "Excessive sale",
        },
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Insufficient stock"

    # Stock must remain unchanged
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["quantity"] == 12

    # Only the two successful movements should exist
    response = client.get(movement_url)
    assert response.status_code == 200

    history = response.json()
    assert len(history) == 2
    assert history[0]["quantity_change"] == -3
    assert history[0]["reason"] == "Customer sale"
    assert history[1]["quantity_change"] == 5
    assert history[1]["reason"] == "Supplier delivery"

    assert all(
        movement["product_id"] == product_id
        for movement in history
    )

def test_product_with_stock_history_cannot_be_deleted(client):
    response = client.post(
        "/products",
        json={
            "name": "Protected Product",
            "sku": f"TEST-{uuid4().hex}",
            "quantity": 10,
        },
    )
    assert response.status_code == 201
    product_id = response.json()["id"]

    response = client.post(
        f"/products/{product_id}/stock-movements",
        json={
            "quantity_change": 5,
            "reason": "Supplier delivery",
        },
    )
    assert response.status_code == 201

    response = client.delete(f"/products/{product_id}")

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Cannot delete a product with stock history"
    )

    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["quantity"] == 15

    response = client.get(
        f"/products/{product_id}/stock-movements"
    )
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_put_cannot_change_quantity(client):
    product_data = {
        "name": "Quantity Test",
        "sku": f"TEST-{uuid4().hex}",
        "quantity": 10,
    }

    response = client.post("/products", json=product_data)
    assert response.status_code == 201
    product_id = response.json()["id"]

    response = client.put(
        f"/products/{product_id}",
        json={**product_data, "quantity": 25},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Use stock movements to change quantity"
    )

    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["quantity"] == 10

def test_low_stock_report(client):
    unique_text = uuid4().hex
    created_ids = {}

    for quantity in [8, 5, 2]:
        response = client.post(
            "/products",
            json={
                "name": f"Stock Report {unique_text} {quantity}",
                "sku": f"{unique_text}-{quantity}",
                "quantity": quantity,
            },
        )

        assert response.status_code == 201
        created_ids[quantity] = response.json()["id"]

    response = client.get(
        "/products/low-stock",
        params={"threshold": 5, "limit": 100},
    )

    assert response.status_code == 200
    products = response.json()

    # Every returned product must meet the threshold.
    assert all(product["quantity"] <= 5 for product in products)

    # Results must be ordered by quantity, then ID.
    actual_order = [
        (product["quantity"], product["id"])
        for product in products
    ]
    assert actual_order == sorted(actual_order)

    returned_ids = {product["id"] for product in products}

    assert created_ids[2] in returned_ids
    assert created_ids[5] in returned_ids
    assert created_ids[8] not in returned_ids