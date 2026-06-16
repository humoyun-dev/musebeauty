"""Admin panel (api/admin) so'rov/javob sxemalari."""
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ─────────────────────────── Auth ───────────────────────────
class LoginIn(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AdminOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: str
    is_active: bool


# ─────────────────────────── Kategoriya ───────────────────────────
class CategoryCreate(BaseModel):
    name: str
    slug: str | None = None
    is_active: bool = True


class CategoryUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    is_active: bool | None = None


# ─────────────────────────── Mahsulot ───────────────────────────
class ProductCreate(BaseModel):
    name: str
    category_id: int | None = None
    description: str | None = None
    image_url: str | None = None
    gallery: list[str] = Field(default_factory=list)   # rasmlar ([0] = muqova)
    price: Decimal = Field(ge=0)
    cost_price: Decimal = Field(default=Decimal("0"), ge=0)
    stock_qty: int = Field(default=0, ge=0)
    is_active: bool = True


class ProductUpdate(BaseModel):
    name: str | None = None
    category_id: int | None = None
    description: str | None = None
    image_url: str | None = None
    gallery: list[str] | None = None
    price: Decimal | None = Field(default=None, ge=0)
    cost_price: Decimal | None = Field(default=None, ge=0)
    stock_qty: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class ProductAdminOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int | None
    name: str
    description: str | None
    image_url: str | None
    gallery: list[str]
    price: Decimal
    cost_price: Decimal
    stock_qty: int
    is_active: bool


# ─────────────────────────── Ta'minot partiyasi ───────────────────────────
class SupplyItemIn(BaseModel):
    product_id: int
    qty: int = Field(ge=1)
    unit_cost: Decimal = Field(ge=0)


class SupplyBatchCreate(BaseModel):
    supplier: str | None = None
    arrival_date: date | None = None
    note: str | None = None
    items: list[SupplyItemIn] = Field(min_length=1)


class SupplyBatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    supplier: str | None
    arrival_date: date | None
    total_cost: Decimal
    note: str | None


# ─────────────────────────── Buyurtma ───────────────────────────
class OrderStatusUpdate(BaseModel):
    status: str


class OrderAdminItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    qty: int
    unit_price: Decimal
    cost_price: Decimal


class OrderAdminOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    status: str
    payment_status: str
    district_id: int | None
    address: str | None
    phone: str | None
    latitude: float | None
    longitude: float | None
    subtotal: Decimal
    discount_amount: Decimal
    delivery_fee: Decimal
    total: Decimal
    created_at: datetime
    items: list[OrderAdminItemOut]


# ─────────────────────────── To'lov ───────────────────────────
class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    amount: Decimal
    method: str
    screenshot_url: str | None
    is_confirmed: bool
    confirmed_by: int | None
    confirmed_at: datetime | None
    created_at: datetime


# ─────────────────────────── Mijoz ───────────────────────────
class CustomerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    telegram_id: int
    name: str | None
    phone: str | None
    created_at: datetime


# ─────────────────────────── Chegirma (kodsiz) ───────────────────────────
class DiscountIn(BaseModel):
    name: str
    type: str = "percent"          # percent | fixed
    value: Decimal = Field(ge=0)
    scope: str = "all"             # all | category | product
    target_id: int | None = None
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    is_active: bool = True


class DiscountUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    value: Decimal | None = None
    scope: str | None = None
    target_id: int | None = None
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    is_active: bool | None = None


class DiscountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: str
    value: Decimal
    scope: str
    target_id: int | None
    valid_from: datetime | None
    valid_until: datetime | None
    is_active: bool


# ─────────────────────────── Promokod (kodli) ───────────────────────────
class PromoIn(BaseModel):
    code: str
    type: str = "percent"          # percent | fixed | free_delivery
    value: Decimal = Field(default=Decimal("0"), ge=0)
    min_order_amount: Decimal = Field(default=Decimal("0"), ge=0)
    max_discount: Decimal | None = None
    usage_limit: int | None = None
    per_user_limit: int | None = None
    first_order_only: bool = False
    scope: str = "all"
    target_id: int | None = None
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    is_active: bool = True


class PromoUpdate(BaseModel):
    code: str | None = None
    type: str | None = None
    value: Decimal | None = None
    min_order_amount: Decimal | None = None
    max_discount: Decimal | None = None
    usage_limit: int | None = None
    per_user_limit: int | None = None
    first_order_only: bool | None = None
    scope: str | None = None
    target_id: int | None = None
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    is_active: bool | None = None


class PromoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    type: str
    value: Decimal
    min_order_amount: Decimal
    max_discount: Decimal | None
    usage_limit: int | None
    used_count: int
    per_user_limit: int | None
    first_order_only: bool
    scope: str
    target_id: int | None
    valid_from: datetime | None
    valid_until: datetime | None
    is_active: bool
