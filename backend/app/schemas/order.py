"""Buyurtma so'rov/javob sxemalari (api/public uchun)."""
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    qty: int
    unit_price: Decimal


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    payment_status: str
    subtotal: Decimal
    discount_amount: Decimal
    delivery_fee: Decimal
    total: Decimal
    address: str | None
    phone: str | None
    latitude: float | None = None
    longitude: float | None = None
    items: list[OrderItemOut]


class OrderItemIn(BaseModel):
    product_id: int
    qty: int = Field(ge=1)


class OrderCreateIn(BaseModel):
    """Website yoki tashqi kanal to'g'ridan-to'g'ri buyurtma berса."""

    telegram_id: int
    items: list[OrderItemIn] = Field(min_length=1)
    district_id: int | None = None
    address: str | None = None
    phone: str | None = None
    promo_code: str | None = None


class DistrictOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    delivery_fee: Decimal


# ─── Website checkout (Telegram'siz) ───
class WebOrderIn(BaseModel):
    name: str | None = None
    phone: str = Field(min_length=7)
    items: list[OrderItemIn] = Field(min_length=1)
    district_id: int | None = None
    address: str | None = None
    promo_code: str | None = None
    # Aniq joylashuv: brauzer geolokatsiyasidan (lat/lng) yoki map havola (parse qilinadi)
    latitude: float | None = None
    longitude: float | None = None
    map_link: str | None = None


class WebOrderOut(BaseModel):
    order_id: int
    total: Decimal
    status: str
    # To'lov ko'rsatmalari
    payment_card_number: str
    payment_card_holder: str
    payme_url: str | None = None   # Payme yoqilgan bo'lsa — to'g'ridan to'lov tugmasi


# Narx oldindan ko'rish (savatda) — checkout'dan oldin
class QuoteLineOut(BaseModel):
    product_id: int
    name: str
    qty: int
    unit_price: Decimal
    line_total: Decimal


class QuoteOut(BaseModel):
    lines: list[QuoteLineOut]
    subtotal: Decimal
    discount_amount: Decimal
    delivery_fee: Decimal
    free_delivery: bool
    total: Decimal
    promo_error: str | None = None


class QuoteIn(BaseModel):
    items: list[OrderItemIn] = Field(min_length=1)
    district_id: int | None = None
    promo_code: str | None = None
    phone: str | None = None   # promokod per-user/first-order tekshiruvi uchun
