"""Buyurtma modellari: orders, order_items.

Snapshot tamoyili: narx, tannarx, chegirma — buyurtma yaratilgan paytdagi
qiymat bilan yoziladi. Keyin mahsulot narxi o'zgarsa, eski buyurtma buzilmaydi.
"""
from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import (
    Money,
    MoneyT,
    OrderStatus,
    PaymentStatus,
    TimestampMixin,
)

# Koordinatalar: 6 kasr ~0.1m aniqlik (lat ±90, lng ±180)
Coord = Numeric(9, 6)


class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="RESTRICT"), index=True
    )

    status: Mapped[str] = mapped_column(
        String(20), default=OrderStatus.NEW.value, nullable=False, index=True
    )
    payment_status: Mapped[str] = mapped_column(
        String(20), default=PaymentStatus.UNPAID.value, nullable=False
    )

    # Yetkazib berish manzili
    district_id: Mapped[int | None] = mapped_column(
        ForeignKey("districts.id", ondelete="SET NULL")
    )
    address: Mapped[str | None] = mapped_column(Text)
    phone: Mapped[str | None] = mapped_column(String(30))
    # Aniq joylashuv (Telegram lokatsiya / Google / Yandex havola orqali)
    latitude: Mapped[Decimal | None] = mapped_column(Coord)
    longitude: Mapped[Decimal | None] = mapped_column(Coord)

    # Narx snapshot'i
    subtotal: Mapped[MoneyT] = mapped_column(Money, default=0, nullable=False)        # chegirmasiz jami
    discount_amount: Mapped[MoneyT] = mapped_column(Money, default=0, nullable=False)  # qo'llanilgan chegirma
    promo_code_id: Mapped[int | None] = mapped_column(
        ForeignKey("promo_codes.id", ondelete="SET NULL")
    )
    delivery_fee: Mapped[MoneyT] = mapped_column(Money, default=0, nullable=False)
    total: Mapped[MoneyT] = mapped_column(Money, default=0, nullable=False)            # subtotal − discount + delivery

    customer: Mapped["Customer"] = relationship(back_populates="orders")  # noqa: F821
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )
    payments: Mapped[list["Payment"]] = relationship(back_populates="order")  # noqa: F821


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), index=True
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"), index=True
    )
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    # Snapshot — sotilgan paytdagi qiymatlar
    unit_price: Mapped[MoneyT] = mapped_column(Money, nullable=False)
    cost_price: Mapped[MoneyT] = mapped_column(Money, default=0, nullable=False)

    order: Mapped["Order"] = relationship(back_populates="items")
