"""Ombor servisi — qoldiqni qulflab kamaytirish/oshirish (oversell oldini olish).

Buyurtma yaratilganda mahsulot qatorlari `SELECT ... FOR UPDATE` bilan qulflanadi
(faqat PostgreSQL'da; SQLite o'zi yozishni serialize qiladi). Shu tranzaksiya
ichida qoldiq tekshiriladi va kamaytiriladi — ikki mijoz bir vaqtda oxirgi donani
ololmaydi.
"""
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import BatchItem, Product, SupplyBatch


class InsufficientStock(Exception):
    """Qoldiq yetarli emas."""

    def __init__(self, product: Product, requested: int):
        self.product = product
        self.requested = requested
        super().__init__(
            f"'{product.name}' uchun qoldiq yetarli emas "
            f"(bor: {product.stock_qty}, so'ralди: {requested})"
        )


class ProductUnavailable(Exception):
    """Mahsulot topilmadi yoki nofaol."""

    def __init__(self, product_id: int):
        self.product_id = product_id
        super().__init__(f"Mahsulot mavjud emas (id={product_id})")


async def lock_products(
    session: AsyncSession, product_ids: list[int]
) -> dict[int, Product]:
    """Berilgan mahsulotlarni qulflab oladi (PostgreSQL). {id: Product} qaytaradi."""
    if not product_ids:
        return {}
    stmt = select(Product).where(Product.id.in_(product_ids))
    if not settings.is_sqlite:
        stmt = stmt.with_for_update()
    rows = (await session.execute(stmt)).scalars().all()
    return {p.id: p for p in rows}


async def reserve(session: AsyncSession, items: dict[int, int]) -> dict[int, Product]:
    """Qoldiqni tekshiradi va kamaytiradi (qulflangan holatda).

    items: {product_id: qty}. Muvaffaqiyatda {id: Product} (yangilangan qoldiq bilan).
    Xato: ProductUnavailable / InsufficientStock (commit chaqiruvchida bo'ladi).
    """
    products = await lock_products(session, list(items.keys()))
    for pid, qty in items.items():
        product = products.get(pid)
        if product is None or not product.is_active:
            raise ProductUnavailable(pid)
        if product.stock_qty < qty:
            raise InsufficientStock(product, qty)
    # Hammasi joyida — kamaytiramiz
    for pid, qty in items.items():
        products[pid].stock_qty -= qty
    return products


async def release(session: AsyncSession, items: dict[int, int]) -> None:
    """Qoldiqni qaytaradi (buyurtma bekor qilinganda)."""
    products = await lock_products(session, list(items.keys()))
    for pid, qty in items.items():
        if pid in products:
            products[pid].stock_qty += qty


def _weighted_average(
    old_qty: int, old_cost: Decimal, add_qty: int, add_cost: Decimal
) -> Decimal:
    """Yangi o'rtacha tannarx (loyiha qarori: O'RTACHA, FIFO emas).

    new_avg = (old_qty*old_cost + add_qty*add_cost) / (old_qty + add_qty)
    """
    total_qty = old_qty + add_qty
    if total_qty <= 0:
        return add_cost
    total_value = (Decimal(old_qty) * old_cost) + (Decimal(add_qty) * add_cost)
    avg = total_value / Decimal(total_qty)
    return avg.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


async def receive_supply_batch(
    session: AsyncSession,
    *,
    supplier: str | None,
    arrival_date: date | None,
    note: str | None,
    items: list[dict],  # [{product_id, qty, unit_cost}]
) -> SupplyBatch:
    """Koreadan kelgan partiyani kiritadi: qoldiqni oshiradi va har mahsulotning
    O'RTACHA tannarxini qayta hisoblaydi. Hammasi bitta tranzaksiyada.
    """
    if not items:
        raise ValueError("Partiyada kamida bitta mahsulot bo'lishi kerak")

    product_ids = [int(it["product_id"]) for it in items]
    products = await lock_products(session, product_ids)

    total_cost = Decimal("0")
    batch = SupplyBatch(supplier=supplier, arrival_date=arrival_date, note=note)

    for it in items:
        pid = int(it["product_id"])
        qty = int(it["qty"])
        unit_cost = Decimal(str(it["unit_cost"]))
        product = products.get(pid)
        if product is None:
            raise ProductUnavailable(pid)

        # O'rtacha tannarxni yangilaymiz, keyin qoldiqni oshiramiz
        product.cost_price = _weighted_average(
            product.stock_qty, Decimal(product.cost_price or 0), qty, unit_cost
        )
        product.stock_qty += qty

        batch.items.append(BatchItem(product_id=pid, qty=qty, unit_cost=unit_cost))
        total_cost += Decimal(qty) * unit_cost

    batch.total_cost = total_cost
    session.add(batch)
    await session.commit()
    await session.refresh(batch)
    return batch
