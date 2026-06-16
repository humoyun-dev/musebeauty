"""Hisobot servisi — savdo, foyda, top mahsulotlar (ERP analitika).

Foyda = (subtotal − chegirma) − tannarx (COGS). Yetkazib berish FOYDAGA
kirmaydi (kuryerga o'tadi). Faqat to'langan (payment_status='tolandi') buyurtmalar.
"""
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Customer,
    Order,
    OrderItem,
    PaymentStatus,
    Payment,
    Product,
)

_PAID = Order.payment_status == PaymentStatus.PAID.value


async def _revenue_profit(session: AsyncSession, *, since: datetime | None, until: datetime | None) -> dict:
    """To'langan buyurtmalar bo'yicha: soni, daromad (total), foyda."""
    conds = [_PAID]
    if since is not None:
        conds.append(Order.created_at >= since)
    if until is not None:
        conds.append(Order.created_at < until)

    # Buyurtmalar soni va daromad
    head = (
        await session.execute(
            select(
                func.count(Order.id),
                func.coalesce(func.sum(Order.total), 0),
                func.coalesce(func.sum(Order.subtotal), 0),
                func.coalesce(func.sum(Order.discount_amount), 0),
            ).where(*conds)
        )
    ).one()
    orders_count, revenue, subtotal, discount = head

    # COGS — order_items bo'yicha tannarx*miqdor (faqat to'langan buyurtmalar)
    cogs = (
        await session.execute(
            select(func.coalesce(func.sum(OrderItem.cost_price * OrderItem.qty), 0))
            .select_from(OrderItem)
            .join(Order, OrderItem.order_id == Order.id)
            .where(*conds)
        )
    ).scalar_one()

    profit = Decimal(subtotal) - Decimal(discount) - Decimal(cogs)
    return {
        "orders_count": int(orders_count),
        "revenue": Decimal(revenue),
        "profit": profit,
        "cogs": Decimal(cogs),
        "discount_total": Decimal(discount),
    }


async def daily_sales(session: AsyncSession, day: date | None = None) -> dict:
    """Bir kunlik savdo (default — bugun)."""
    if day is None:
        day = datetime.now(timezone.utc).date()
    since = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    until = since + timedelta(days=1)
    data = await _revenue_profit(session, since=since, until=until)
    data["date"] = day.isoformat()
    return data


async def top_products(
    session: AsyncSession, *, limit: int = 10, days: int | None = None
) -> list[dict]:
    """Eng ko'p sotilgan mahsulotlar (to'langan buyurtmalar bo'yicha)."""
    conds = [_PAID]
    if days is not None:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        conds.append(Order.created_at >= since)

    stmt = (
        select(
            OrderItem.product_id,
            Product.name,
            func.sum(OrderItem.qty).label("qty_sold"),
            func.sum(OrderItem.unit_price * OrderItem.qty).label("revenue"),
        )
        .join(Order, OrderItem.order_id == Order.id)
        .join(Product, OrderItem.product_id == Product.id)
        .where(*conds)
        .group_by(OrderItem.product_id, Product.name)
        .order_by(func.sum(OrderItem.qty).desc())
        .limit(limit)
    )
    rows = (await session.execute(stmt)).all()
    return [
        {
            "product_id": r.product_id,
            "name": r.name,
            "qty_sold": int(r.qty_sold),
            "revenue": Decimal(r.revenue),
        }
        for r in rows
    ]


async def dashboard(session: AsyncSession) -> dict:
    """Admin bosh sahifa ko'rsatkichlari."""
    now = datetime.now(timezone.utc)
    today = await daily_sales(session, now.date())

    month_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
    month = await _revenue_profit(session, since=month_start, until=None)

    total_customers = await session.scalar(select(func.count()).select_from(Customer))
    active_products = await session.scalar(
        select(func.count()).select_from(Product).where(Product.is_active.is_(True))
    )
    low_stock = await session.scalar(
        select(func.count())
        .select_from(Product)
        .where(Product.is_active.is_(True), Product.stock_qty < 5)
    )
    pending_payments = await session.scalar(
        select(func.count()).select_from(Payment).where(Payment.is_confirmed.is_(False))
    )

    return {
        "today": today,
        "month": month,
        "total_customers": int(total_customers or 0),
        "active_products": int(active_products or 0),
        "low_stock_count": int(low_stock or 0),
        "pending_payments": int(pending_payments or 0),
    }


async def low_stock_products(session: AsyncSession, *, threshold: int = 5) -> list[Product]:
    stmt = (
        select(Product)
        .where(Product.is_active.is_(True), Product.stock_qty < threshold)
        .order_by(Product.stock_qty)
    )
    return list((await session.execute(stmt)).scalars().all())
