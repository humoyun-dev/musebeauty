"""Buyurtma servisi — savatdan buyurtma yaratish (atomik) va holat o'zgartirish.

create_order_from_cart BITTA tranzaksiyada:
  qoldiqni qulflaydi → tekshiradi → kamaytiradi → narxni snapshot qiladi →
  Order + OrderItem yaratadi → commit. Xato bo'lsa hammasi rollback (qoldiq buzilmaydi).
"""
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    Customer,
    District,
    Order,
    OrderItem,
    OrderStatus,
    PaymentStatus,
    PromoCode,
    PromoRedemption,
)
from app.services import inventory, pricing


class EmptyCart(Exception):
    pass


# Buyurtma holati o'tishlari (faqat ruxsat etilgan zanjir)
_ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    OrderStatus.NEW.value: {OrderStatus.PAID.value, OrderStatus.CANCELLED.value},
    OrderStatus.PAID.value: {OrderStatus.PREPARED.value, OrderStatus.CANCELLED.value},
    OrderStatus.PREPARED.value: {OrderStatus.SHIPPED.value, OrderStatus.CANCELLED.value},
    OrderStatus.SHIPPED.value: {OrderStatus.DELIVERED.value, OrderStatus.RETURNED.value},
    OrderStatus.DELIVERED.value: {OrderStatus.RETURNED.value},
}


class InvalidStatusTransition(Exception):
    def __init__(self, current: str, target: str):
        super().__init__(f"Holatni '{current}' → '{target}' ga o'zgartirib bo'lmaydi")


def allowed_next(status: str) -> list[str]:
    """Joriy holatdan ruxsat etilgan keyingi holatlar (admin bot tugmalari uchun)."""
    return sorted(_ALLOWED_TRANSITIONS.get(status, set()))


async def create_order_from_cart(
    session: AsyncSession,
    *,
    customer: Customer,
    items: dict[int, int],
    district_id: int | None,
    address: str | None,
    phone: str | None,
    promo_code: str | None = None,
    latitude: Decimal | float | None = None,
    longitude: Decimal | float | None = None,
) -> Order:
    """Savat (items) dan buyurtma yaratadi (atomik).

    Qoldiqni qulflab kamaytiradi, narxni snapshot qiladi, promokodni (agar bor va
    foydaliroq bo'lsa) qo'llaydi va promo_redemptions ga yozadi. Promokod commit
    paytida QAYTA tekshiriladi (race oldini olish) — yaroqsiz bo'lsa PromoError.
    """
    from app.services.promo import PromoValidation, validate_promo

    if not items:
        raise EmptyCart()

    # 1) Qoldiqni qulflab tekshiramiz va kamaytiramiz (oversell yo'q)
    products = await inventory.reserve(session, items)  # xato → ProductUnavailable/InsufficientStock

    # 2) Promokod (commit paytida qayta validatsiya)
    subtotal = sum(
        (Decimal(products[pid].price) * qty for pid, qty in items.items()), Decimal("0")
    )
    promo_val: PromoValidation | None = None
    if promo_code:
        promo_val = await validate_promo(
            session,
            code=promo_code,
            customer=customer,
            products=products,
            items=items,
            subtotal=subtotal,
        )

    # 3) Narx: auto-chegirma vs promokod — bittasi (foydaliroq)
    district = await session.get(District, district_id) if district_id else None
    auto = await pricing.best_auto_discount(session, products, items)
    quote = pricing.compute_quote(products, items, district, auto_discount=auto, promo=promo_val)

    # 4) Buyurtma + qatorlar (narx/tannarx snapshot bilan)
    order = Order(
        customer_id=customer.id,
        status=OrderStatus.NEW.value,
        payment_status=PaymentStatus.UNPAID.value,
        district_id=district_id,
        address=address,
        phone=phone or customer.phone,
        latitude=Decimal(str(latitude)) if latitude is not None else None,
        longitude=Decimal(str(longitude)) if longitude is not None else None,
        subtotal=quote.subtotal,
        discount_amount=quote.discount_amount,
        promo_code_id=quote.promo_code_id,
        delivery_fee=quote.delivery_fee,
        total=quote.total,
    )
    order.items = [
        OrderItem(
            product_id=line.product_id,
            qty=line.qty,
            unit_price=line.unit_price,
            cost_price=line.cost_price,
        )
        for line in quote.lines
    ]
    session.add(order)
    await session.flush()  # order.id olish uchun

    # 5) Promokod g'olib bo'lsa — redemption yozamiz va used_count oshiramiz
    if quote.discount_source == "promo" and promo_val is not None:
        # Foyda: free_delivery'da saqlangan yetkazib berish, aks holda subtotal chegirmasi
        if promo_val.free_delivery:
            benefit = Decimal(district.delivery_fee) if district else Decimal("0")
        else:
            benefit = quote.discount_amount
        session.add(
            PromoRedemption(
                promo_code_id=promo_val.promo_code.id,
                customer_id=customer.id,
                order_id=order.id,
                discount_amount=benefit,
                used_at=datetime.now(timezone.utc),
            )
        )
        promo_obj = await session.get(PromoCode, promo_val.promo_code.id)
        if promo_obj is not None:
            promo_obj.used_count = (promo_obj.used_count or 0) + 1

    await session.commit()
    await session.refresh(order)
    return order


async def get_order(session: AsyncSession, order_id: int) -> Order | None:
    stmt = (
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items))
    )
    return (await session.execute(stmt)).scalar_one_or_none()


async def list_orders(
    session: AsyncSession,
    *,
    status: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Order]:
    """Admin: barcha buyurtmalar (ixtiyoriy holat filtri bilan)."""
    stmt = select(Order).options(selectinload(Order.items)).order_by(Order.created_at.desc())
    if status:
        stmt = stmt.where(Order.status == status)
    stmt = stmt.limit(limit).offset(offset)
    return list((await session.execute(stmt)).scalars().all())


async def list_customer_orders(
    session: AsyncSession, customer_id: int, *, limit: int = 20
) -> list[Order]:
    stmt = (
        select(Order)
        .where(Order.customer_id == customer_id)
        .order_by(Order.created_at.desc())
        .limit(limit)
    )
    return list((await session.execute(stmt)).scalars().all())


async def set_status(session: AsyncSession, order_id: int, target: str) -> Order:
    """Holatni ruxsat etilgan zanjir bo'yicha o'zgartiradi.

    Bekor/qaytarilganda qoldiq omborga qaytariladi.
    """
    order = await get_order(session, order_id)
    if order is None:
        raise ValueError(f"Buyurtma topilmadi (id={order_id})")

    if target == order.status:
        return order
    allowed = _ALLOWED_TRANSITIONS.get(order.status, set())
    if target not in allowed:
        raise InvalidStatusTransition(order.status, target)

    # Bekor/qaytarish → qoldiqni qaytaramiz
    if target in (OrderStatus.CANCELLED.value, OrderStatus.RETURNED.value):
        await inventory.release(
            session, {item.product_id: item.qty for item in order.items}
        )

    order.status = target
    if target == OrderStatus.PAID.value:
        order.payment_status = PaymentStatus.PAID.value
    await session.commit()
    await session.refresh(order)
    return order
