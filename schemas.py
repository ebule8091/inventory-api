from pydantic import BaseModel, ConfigDict, Field
from pydantic import field_validator
from datetime import datetime

class ProductCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    sku: str = Field(min_length=1, max_length=50)
    quantity: int = Field(ge=0)


class ProductResponse(ProductCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)

class StockMovementCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    quantity_change: int
    reason: str = Field(min_length=1, max_length=200)

    @field_validator("quantity_change")
    @classmethod
    def reject_zero_change(cls, value: int) -> int:
        if value == 0:
            raise ValueError("Quantity change cannot be zero")
        return value

class StockMovementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity_change: int
    reason: str
    created_at: datetime