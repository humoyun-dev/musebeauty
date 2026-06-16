"""Aksiyalar (promotions) — public ko'rinishdagi chegirma va promokodlar."""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PublicDiscount(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: str           # percent | fixed
    value: Decimal
    scope: str          # all | category | product
    target_id: int | None
    valid_until: datetime | None


class PublicPromo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    type: str           # percent | fixed | free_delivery
    value: Decimal
    min_order_amount: Decimal
    max_discount: Decimal | None
    first_order_only: bool
    valid_until: datetime | None


class PromotionsOut(BaseModel):
    discounts: list[PublicDiscount]
    promo_codes: list[PublicPromo]
