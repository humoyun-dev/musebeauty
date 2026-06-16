"""Modellar uchun umumiy yordamchilar: timestamp mixin, pul tipi, enum'lar.

Pul: Numeric(12, 2) — so'mda butun ishlatiladi, lekin Numeric float xatosini
oldini oladi va kelajakda tiyin/kasr kerak bo'lsa tayyor turadi.
Enum'lar: String ustunda saqlanadi (native DB enum emas) — Alembic sodda,
SQLite (dev) bilan ham mos. Ruxsat etilgan qiymatlar shu yerda hujjatlangan.
"""
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import DateTime, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column

# Pul ustuni uchun qayta ishlatiladigan tip
Money = Numeric(12, 2)
MoneyT = Decimal  # Python tomonda


class TimestampMixin:
    """created_at ustunini qo'shadi (baza tomonda avtomatik to'ldiriladi)."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


# ─────────────────────────── Enum'lar ───────────────────────────
class OrderStatus(StrEnum):
    NEW = "yangi"
    PAID = "tolandi"
    PREPARED = "tayyorlandi"
    SHIPPED = "jonatildi"
    DELIVERED = "yetkazildi"
    CANCELLED = "bekor_qilindi"
    RETURNED = "qaytarildi"


class PaymentStatus(StrEnum):
    UNPAID = "tolanmagan"
    PAID = "tolandi"
    REFUNDED = "qaytarildi"


class PaymentMethod(StrEnum):
    MANUAL_CARD = "karta_qolda"  # Humo/Uzcard chek
    PAYME = "payme"
    CLICK = "click"


class DiscountType(StrEnum):
    PERCENT = "percent"
    FIXED = "fixed"


class PromoType(StrEnum):
    PERCENT = "percent"
    FIXED = "fixed"
    FREE_DELIVERY = "free_delivery"


class Scope(StrEnum):
    ALL = "all"
    CATEGORY = "category"
    PRODUCT = "product"


class AdminRole(StrEnum):
    SUPERADMIN = "superadmin"
    MANAGER = "manager"
    OPERATOR = "operator"
