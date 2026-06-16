"""Narx hisobi servisi — chegirma + promokod + yetkazib berish.

LOYIHA QARORI: chegirma va promokod USTMA-UST EMAS — faqat BITTASI qo'llanadi,
mijozga FOYDALIROQ bo'lgani (jami summani ko'proq kamaytirgani). Tartib:
  subtotal → (eng yaxshi auto-chegirma) vs (promokod) → bittasi → yetkazib berish.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Discount, District, DiscountType, Product
from app.services.promo import PromoValidation, scoped_subtotal


@dataclass
class QuoteLine:
    product_id: int
    name: str
    qty: int
    unit_price: Decimal
    cost_price: Decimal

    @property
    def line_total(self) -> Decimal:
        return self.unit_price * self.qty


@dataclass
class PriceQuote:
    lines: list[QuoteLine] = field(default_factory=list)
    subtotal: Decimal = Decimal("0")
    discount_amount: Decimal = Decimal("0")
    discount_source: str | None = None     # "auto" | "promo" | None
    promo_code_id: int | None = None
    free_delivery: bool = False
    delivery_fee: Decimal = Decimal("0")
    total: Decimal = Decimal("0")


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def list_active_discounts(session: AsyncSession) -> list[Discount]:
    """Hozir amal qiladigan avtomatik (kodsiz) chegirmalar — "Aksiyalar" uchun."""
    now = _now()
    stmt = (
        select(Discount)
        .where(
            Discount.is_active.is_(True),
            or_(Discount.valid_from.is_(None), Discount.valid_from <= now),
            or_(Discount.valid_until.is_(None), Discount.valid_until >= now),
        )
        .order_by(Discount.id.desc())
    )
    return list((await session.execute(stmt)).scalars().all())


async def best_auto_discount(
    session: AsyncSession, products: dict[int, Product], items: dict[int, int]
) -> Decimal:
    """Savatga mos eng katta avtomatik (kodsiz) chegirma summasi."""
    now = _now()
    stmt = select(Discount).where(
        Discount.is_active.is_(True),
        or_(Discount.valid_from.is_(None), Discount.valid_from <= now),
        or_(Discount.valid_until.is_(None), Discount.valid_until >= now),
    )
    discounts = (await session.execute(stmt)).scalars().all()

    best = Decimal("0")
    for d in discounts:
        base = scoped_subtotal(products, items, d.scope, d.target_id)
        if base <= 0:
            continue
        if d.type == DiscountType.PERCENT.value:
            amount = (base * Decimal(d.value) / Decimal(100)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        else:  # fixed
            amount = min(Decimal(d.value), base)
        best = max(best, amount)
    return best


def compute_quote(
    products: dict[int, Product],
    items: dict[int, int],
    district: District | None,
    *,
    auto_discount: Decimal = Decimal("0"),
    promo: PromoValidation | None = None,
) -> PriceQuote:
    """Yakuniy narx — auto-chegirma va promokoddan BITTASI (foydaliroq) qo'llanadi."""
    q = PriceQuote()
    for pid, qty in items.items():
        product = products[pid]
        line = QuoteLine(
            product_id=pid,
            name=product.name,
            qty=qty,
            unit_price=Decimal(product.price),
            cost_price=Decimal(product.cost_price or 0),
        )
        q.lines.append(line)
        q.subtotal += line.line_total

    base_delivery = Decimal(district.delivery_fee) if district else Decimal("0")

    # Har variantning JAMI kamaytirishini hisoblaymiz va kattasini tanlaymiz
    auto_reduction = auto_discount
    promo_reduction = Decimal("0")
    if promo is not None:
        promo_reduction = promo.discount_amount + (
            base_delivery if promo.free_delivery else Decimal("0")
        )

    if promo is not None and promo_reduction > 0 and promo_reduction >= auto_reduction:
        q.discount_source = "promo"
        q.discount_amount = promo.discount_amount
        q.free_delivery = promo.free_delivery
        q.promo_code_id = promo.promo_code.id
    elif auto_reduction > 0:
        q.discount_source = "auto"
        q.discount_amount = auto_reduction

    q.delivery_fee = Decimal("0") if q.free_delivery else base_delivery
    q.total = q.subtotal - q.discount_amount + q.delivery_fee
    if q.total < 0:
        q.total = Decimal("0")
    return q


async def quote(
    session: AsyncSession,
    items: dict[int, int],
    district_id: int | None,
    *,
    customer=None,
    promo_code: str | None = None,
) -> tuple[PriceQuote, str | None]:
    """Ko'rsatish uchun narx. (quote, promo_error) qaytaradi.

    promo_error — promokod yaroqsiz bo'lsa sababi (bot mijozga ko'rsatadi);
    bunda promokod e'tiborga olinmaydi, lekin auto-chegirma baribir qo'llanadi.
    """
    from app.services import catalog  # aylanma importdan qochish
    from app.services.promo import PromoError, validate_promo

    products: dict[int, Product] = {}
    for pid in items:
        product = await catalog.get_product(session, pid)
        if product:
            products[pid] = product
    valid_items = {pid: qty for pid, qty in items.items() if pid in products}
    district = await session.get(District, district_id) if district_id else None

    subtotal = sum(
        (Decimal(products[pid].price) * qty for pid, qty in valid_items.items()),
        Decimal("0"),
    )
    auto = await best_auto_discount(session, products, valid_items)

    promo_val: PromoValidation | None = None
    promo_error: str | None = None
    if promo_code:
        try:
            promo_val = await validate_promo(
                session,
                code=promo_code,
                customer=customer,   # None bo'lsa per-user/first-order o'tkaziladi (preview)
                products=products,
                items=valid_items,
                subtotal=subtotal,
            )
        except PromoError as exc:
            promo_error = str(exc)

    return compute_quote(products, valid_items, district, auto_discount=auto, promo=promo_val), promo_error
