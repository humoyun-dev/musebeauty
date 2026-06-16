"""Barcha modellarni bir joyga yig'amiz.

Muhim: Alembic va relationship'lar to'g'ri ishlashi uchun HAR BIR model shu
yerdan import qilinishi shart (aks holda Base.metadata to'liq bo'lmaydi).
"""
from app.core.database import Base
from app.models.admin import Admin, AuditLog
from app.models.base import (
    AdminRole,
    DiscountType,
    OrderStatus,
    PaymentMethod,
    PaymentStatus,
    PromoType,
    Scope,
)
from app.models.catalog import BatchItem, Category, Product, SupplyBatch
from app.models.customer import Customer, District
from app.models.order import Order, OrderItem
from app.models.payment import Payment
from app.models.promo import Discount, PromoCode, PromoRedemption
from app.models.provider import PaymeTransaction

__all__ = [
    "Base",
    # katalog / ombor
    "Category",
    "Product",
    "SupplyBatch",
    "BatchItem",
    # mijoz
    "Customer",
    "District",
    # buyurtma
    "Order",
    "OrderItem",
    # to'lov
    "Payment",
    # marketing
    "Discount",
    "PromoCode",
    "PromoRedemption",
    # to'lov provayderlari
    "PaymeTransaction",
    # admin
    "Admin",
    "AuditLog",
    # enum'lar
    "OrderStatus",
    "PaymentStatus",
    "PaymentMethod",
    "DiscountType",
    "PromoType",
    "Scope",
    "AdminRole",
]
