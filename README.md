# Inventory Management API

A Python backend project built with FastAPI and MySQL.
It supports product management, name search, pagination,
input validation, and automated tests.

## Technology Stack

- Python and FastAPI
- MySQL
- SQLAlchemy and PyMySQL
- Pydantic
- pytest and HTTPX

## Features

- Create products with unique SKUs
- List products with search and pagination
- Retrieve a product by ID
- Update product information
- Delete products
- Reject negative quantities and duplicate SKUs
- Store products permanently in MySQL

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Return a welcome message |
| POST | `/products` | Create a product |
| GET | `/products` | List and search products |
| GET | `/products/{product_id}` | Retrieve one product |
| PUT | `/products/{product_id}` | Update all product fields |
| DELETE | `/products/{product_id}` | Delete a product |

Example search:

`/products?search=keyboard&offset=0&limit=10`

## Local Setup

### 1. Create a virtual environment

Open a terminal inside the project folder:

```powershell
py -m venv .venv
```

### 2. Install dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. Create the databases

With MySQL Server running, execute in MySQL Workbench:

```sql
CREATE DATABASE IF NOT EXISTS inventory_db;
CREATE DATABASE IF NOT EXISTS inventory_test_db;
```

### 4. Configure the environment

Copy the configuration template:

```powershell
Copy-Item .env.example .env
```

Edit `.env` with your MySQL connection settings.

Keep `DB_NAME=inventory_db` and
`TEST_DB_NAME=inventory_test_db`.

Do not commit `.env` to version control.

### 5. Create application tables

```powershell
.\.venv\Scripts\python.exe create_tables.py
```

### 6. Start the API

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8001
```

Open interactive documentation:

http://127.0.0.1:8001/docs

## Example Product Request

Send this JSON to POST `/products`:

```json
{
  "name": "Wireless Keyboard",
  "sku": "KB-001",
  "quantity": 20
}
```

## Automated Tests

Keep MySQL Server running, then execute:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

Tests cover:

- Home endpoint response
- Rejection of negative quantities
- Product creation, retrieval, update, and deletion
- Rejection of duplicate SKUs

Database tests use `inventory_test_db`.
The test fixture creates missing tables and rolls back
record changes after each test.

## Current Scope

This is a local learning and portfolio project.
Authentication, stock movement history, database migrations,
and deployment are planned improvements.