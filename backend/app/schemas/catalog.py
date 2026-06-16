"""Katalog javob sxemalari (api/public uchun)."""
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    is_active: bool


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int | None
    name: str
    description: str | None
    image_url: str | None
    gallery: list[str] = []
    price: Decimal
    stock_qty: int
    is_active: bool
