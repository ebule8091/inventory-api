from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from schemas import ProductCreate, ProductResponse
from database import get_db
from models import Product

app = FastAPI(title="Inventory Management API")


@app.get("/")
def home():
    return {"message": "Inventory API is running"}


@app.get("/products", response_model=list[ProductResponse])
def get_products(
    search: str | None = Query(default=None, min_length=1),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    statement = select(Product)

    if search is not None:
        statement = statement.where(
            Product.name.contains(search, autoescape=True)
        )

    statement = (
        statement
        .order_by(Product.id)
        .offset(offset)
        .limit(limit)
    )

    return db.scalars(statement).all()


@app.post(
    "/products",
    response_model=ProductResponse,
    status_code=201,
)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
):
    existing_product = db.scalar(
        select(Product).where(Product.sku == product.sku)
    )

    if existing_product is not None:
        raise HTTPException(
            status_code=409,
            detail="A product with this SKU already exists",
        )

    new_product = Product(**product.model_dump())

    db.add(new_product)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Product conflicts with a database constraint",
        )

    db.refresh(new_product)
    return new_product

@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product

@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product: ProductCreate,
    db: Session = Depends(get_db),
):
    existing_product = db.get(Product, product_id)

    if existing_product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    duplicate = db.scalar(
        select(Product).where(
            Product.sku == product.sku,
            Product.id != product_id,
        )
    )

    if duplicate is not None:
        raise HTTPException(
            status_code=409,
            detail="A product with this SKU already exists",
        )

    existing_product.name = product.name
    existing_product.sku = product.sku
    existing_product.quantity = product.quantity

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Product conflicts with a database constraint",
        )

    db.refresh(existing_product)
    return existing_product

@app.delete("/products/{product_id}", status_code=200)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully"}