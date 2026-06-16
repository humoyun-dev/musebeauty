"""Savat so'rov/javob sxemalari (api/public uchun)."""
from decimal import Decimal

from pydantic import BaseModel, Field


class CartItemIn(BaseModel):
    product_id: int
    qty: int = Field(ge=1)


class CartLineOut(BaseModel):
    product_id: int
    name: str
    qty: int
    unit_price: Decimal
    line_total: Decimal


class CartOut(BaseModel):
    lines: list[CartLineOut]
    subtotal: Decimal
    item_count: int
