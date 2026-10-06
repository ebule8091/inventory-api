# Inventory Management API

An inventory backend built with Python, FastAPI, and MySQL.
It provides product management, search, pagination, and stock
movement tracking with input validation and automated tests.

## Technology Stack

- Python
- FastAPI
- MySQL
- SQLAlchemy
- PyMySQL
- Pydantic
- pytest and HTTPX
- Git and GitHub

## Features

- Create products with unique SKUs
- List products with name search and pagination
- Retrieve a product by ID
- Update product names and SKUs
- Delete products without stock history
- Reject negative product quantities and duplicate SKUs
- Trim whitespace and reject blank product names and SKUs
- Store products permanently in MySQL
- Record stock receipts and sales with a reason
- Retrieve stock movement history with pagination
- Reject movements that would make stock negative
- Require quantity changes to use the stock movement endpoint
- Prevent deleting products with stock history

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Return a welcome message |
| POST | `/products` | Create a product |
| GET | `/products` | List and search products |
| GET | `/products/{product_id}` | Retrieve one product |
| PUT | `/products/{product_id}` | Update name and SKU; quantity must remain unchanged |
| DELETE | `/products/{product_id}` | Delete a product without stock history |
| POST | `/products/{product_id}/stock-movements` | Change stock and record the reason |
| GET | `/products/{product_id}/stock-movements` | Retrieve stock movement history |

### Search and Pagination

Example:

```text
/products?search=keyboard&offset=0&limit=10
```

- `search`: Optional text to match within product names.
- `offset`: Number of matching records to skip. Default: `0`.
- `limit`: Maximum records to return. Default: `10`; allowed range: `1–100`.

Products are returned in ascending ID order.
Stock movements are returned in descending ID order.

## Project Files

| File | Responsibility |
|---|---|
| `main.py` | API endpoints and inventory rules |
| `models.py` | SQLAlchemy database models |
| `schemas.py` | Request validation and response models |
| `database.py` | Database configuration, connections, and sessions |
| `create_tables.py` | Initial database table creation |
| `conftest.py` | Test database fixture |
| `test_main.py` | Home endpoint and validation tests |
| `test_products.py` | Product and stock movement tests |
| `requirements.txt` | Python dependencies |
| `.env.example` | Configuration template |
| `.gitignore` | Files excluded from version control |

## Local Setup

These instructions use Windows PowerShell.

### 1. Download the Project

```powershell
git clone https://github.com/ebule8091/inventory-api.git
cd inventory-api
```

### 2. Create a Virtual Environment

```powershell
py -m venv .venv
```

### 3. Install Dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The commands use the virtual environment's Python directly,
so activating the environment is optional.

### 4. Create the MySQL Databases

Ensure MySQL Server is running. Execute the following in
MySQL Workbench:

```sql
CREATE DATABASE IF NOT EXISTS inventory_db;
CREATE DATABASE IF NOT EXISTS inventory_test_db;
```

- `inventory_db`: Application database.
- `inventory_test_db`: Separate database for automated tests.

### 5. Configure the Environment

Copy the configuration template:

```powershell
Copy-Item .env.example .env
```

Edit `.env` with your local MySQL connection settings:

```dotenv
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_mysql_username
DB_PASSWORD="your_mysql_password"
DB_NAME=inventory_db
TEST_DB_NAME=inventory_test_db
```

Replace the username and password placeholders with your
actual local credentials.

Keep `.env` private. It is excluded from Git.
Keep placeholder credentials in `.env.example`.

### 6. Create Application Tables

```powershell
.\.venv\Scripts\python.exe create_tables.py
```

This creates missing tables. It does not migrate changes to
existing table definitions.

### 7. Start the API

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8001
```

Open the interactive API documentation:

http://127.0.0.1:8001/docs

Keep the terminal open while using the API.
Press `Ctrl + C` to stop the server.

## Example Product Request

Send this JSON to POST `/products`:

```json
{
  "name": "Wireless Keyboard",
  "sku": "KB-001",
  "quantity": 20
}
```

The API returns the created product with a
database-generated ID and status `201 Created`.

The quantity supplied when creating a product is its
opening balance. It does not create a stock movement record.

## Updating Product Details

Send all three fields to PUT `/products/{product_id}`:

```json
{
  "name": "Updated Wireless Keyboard",
  "sku": "KB-001",
  "quantity": 20
}
```

The submitted quantity must match the current saved quantity.
Use the stock movement endpoint to change stock.

## Stock Movements

Use POST `/products/{product_id}/stock-movements`
to change an existing product's quantity.

### Receive Stock

```json
{
  "quantity_change": 10,
  "reason": "Supplier delivery"
}
```

### Sell Stock

```json
{
  "quantity_change": -3,
  "reason": "Customer sale"
}
```

Positive values increase stock. Negative values decrease stock.

The stock update and movement record are saved in one
transaction. The product row is locked during the change.
A successful request returns the updated product with
status `201 Created`.

### Inventory Rules

- Quantity changes cannot be zero.
- Reasons must contain nonblank text.
- Stock cannot become negative.
- PUT cannot change product quantity.
- Products with stock history cannot be deleted.

### View History

GET `/products/{product_id}/stock-movements`
returns movement records with the newest first.

Each record includes:

- Movement ID
- Product ID
- Quantity change
- Reason
- Creation timestamp

The endpoint supports `offset` and `limit`.
An existing product without movements returns an empty list.

## Response Codes

| Code | Meaning |
|---|---|
| `200` | Retrieval, update, or deletion succeeded |
| `201` | Product or stock movement created |
| `404` | Product not found |
| `409` | Duplicate SKU or inventory rule conflict |
| `422` | Request validation failed |

## Automated Tests

Ensure MySQL Server is running and `.env` includes:

```dotenv
TEST_DB_NAME=inventory_test_db
```

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

Uvicorn does not need to be running for the tests.

The current suite contains nine tests covering:

- Home endpoint response
- Rejection of negative quantities
- Product creation, retrieval, update, and deletion
- Rejection of duplicate SKUs
- Rejection of blank product names
- Product search and pagination
- Stock receipts, sales, and movement history
- Rejection of sales exceeding available stock
- Prevention of deletion for products with stock history
- Prevention of quantity changes through PUT

Some tests verify multiple behaviors.

Database tests use `inventory_test_db`.
The fixture creates missing test tables and rolls back
record changes after each test. It refuses to use the
application database.

## Verify Data in MySQL Workbench

Run fresh queries to view saved application data:

```sql
SELECT * FROM inventory_db.products;
SELECT * FROM inventory_db.stock_movements;
```

## Current Scope

This is a local learning and portfolio project.
The API currently has no authentication or access controls.

Planned improvements include:

- User authentication and authorization
- Database migrations with Alembic
- Low-stock reporting
- Docker configuration
- Continuous integration
- Deployment