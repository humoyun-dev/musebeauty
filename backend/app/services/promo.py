"""Promokod servisi — kod validatsiyasi va chegirma hisobi.

Loyiha qarori: chegirma + promokod USTMA-UST EMAS (bittasi). Bu yerda faqat
promokodning o'zi tekshiriladi va uning chegirma summasi hisoblanadi; "bittasini
tanlash" mantiqi pricing servisida (auto-chegirma bilan solishtirib).
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Customer,
    Order,
    Product,
    PromoCode,
    PromoRedemption,
    PromoType,
    Scope,
)


class PromoError(Exception):
    """Promokod yaroqsiz — message mijozga ko'rsatiladi."""


async def list_active_promos(session: AsyncSession) -> list[PromoCode]:
    """Hozir amal qiladigan, limiti tugamagan promokodlar — "Aksiyalar" uchun."""
    now = datetime.now(timezone.utc)
    stmt = (
        select(PromoCode)
        .where(
            PromoCode.is_active.is_(True),
            or_(PromoCode.valid_from.is_(None), PromoCode.valid_from <= now),
            or_(PromoCode.valid_until.is_(None), PromoCode.valid_until >= now),
            or_(
                PromoCode.usage_limit.is_(None),
                PromoCode.used_count < PromoCode.usage_limit,
            ),
        )
        .order_by(PromoCode.id.desc())
    )
    return list((await session.execute(stmt)).scalars().all())


@dataclass
class PromoValidation:
    promo_code: PromoCode
    discount_amount: Decimal      # subtotal'ga chegirma (free_delivery'da 0)
    free_delivery: bool           # True bo'lsa yetkazib berish bepul


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _as_aware(dt: datetime | None) -> datetime | None:
    """SQLite naive datetime qaytaradi — UTC deb belgilaymiz (Postgres'da aware keladi).
    Shunday qilib taqqoslash ikkala bazada ham xato bermaydi."""
    if dt is not None and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def scoped_subtotal(
    products: dict[int, Product],
    items: dict[int, int],
    scope: str,
    target_id: int | None,
) -> Decimal:
    """Scope bo'yicha tegishli mahsulotlar summasi (chegirma shu summaga tegadi)."""
    total = Decimal("0")
    for pid, qty in items.items():
        product = products.get(pid)
        if product is None:
            continue
        if scope == Scope.CATEGORY.value and product.category_id != target_id:
            continue
        if scope == Scope.PRODUCT.value and pid != target_id:
            continue
        total += Decimal(product.price) * qty
    return total


async def validate_promo(
    session: AsyncSession,
    *,
    code: str,
    customer: Customer | None,
    products: dict[int, Product],
    items: dict[int, int],
    subtotal: Decimal,
) -> PromoValidation:
    """Promokodni to'liq tekshiradi. Yaroqli bo'lsa PromoValidation, aks holda PromoError."""
    code = code.strip()
    promo = (
        await session.execute(
            select(PromoCode).where(func.lower(PromoCode.code) == code.lower())
        )
    ).scalar_one_or_none()

    if promo is None:
        raise PromoError("Bunday promokod topilmadi")
    if not promo.is_active:
        raise PromoError("Promokod faol emas")

    now = _now()
    valid_from = _as_aware(promo.valid_from)
    valid_until = _as_aware(promo.valid_until)
    if valid_from and valid_from > now:
        raise PromoError("Promokod hali boshlanmagan")
    if valid_until and valid_until < now:
        raise PromoError("Promokod muddati tugagan")

    if promo.usage_limit is not None and promo.used_count >= promo.usage_limit:
        raise PromoError("Promokod ishlatish limiti tugagan")

    if Decimal(promo.min_order_amount or 0) > subtotal:
        raise PromoError(
            f"Promokod uchun minimal summa: {int(promo.min_order_amount)} so'm"
        )

    # Per-user limit (mijoz noma'lum bo'lsa — preview, tekshirilmaydi)
    if promo.per_user_limit is not None and customer is not None:
        used = await session.scalar(
            select(func.count())
            .select_from(PromoRedemption)
            .where(
                PromoRedemption.promo_code_id == promo.id,
                PromoRedemption.customer_id == customer.id,
            )
        )
        if (used or 0) >= promo.per_user_limit:
            raise PromoError("Siz bu promokodni allaqachon ishlatgansiz")

    # Faqat birinchi buyurtma uchun (mijoz noma'lum bo'lsa — preview, o'tkaziladi)
    if promo.first_order_only and customer is not None:
        order_count = await session.scalar(
            select(func.count()).select_from(Order).where(Order.customer_id == customer.id)
        )
        if (order_count or 0) > 0:
            raise PromoError("Promokod faqat birinchi buyurtma uchun")

    # Chegirma summasi
    base = scoped_subtotal(products, items, promo.scope, promo.target_id)
    if base <= 0:
        raise PromoError("Promokod ushbu savatdagi mahsulotlarga tegishli emas")

    free_delivery = False
    discount = Decimal("0")

    if promo.type == PromoType.FREE_DELIVERY.value:
        free_delivery = True
    elif promo.type == PromoType.PERCENT.value:
        discount = (base * Decimal(promo.value) / Decimal(100)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        if promo.max_discount is not None:
            discount = min(discount, Decimal(promo.max_discount))
    elif promo.type == PromoType.FIXED.value:
        discount = min(Decimal(promo.value), base)

    return PromoValidation(promo_code=promo, discount_amount=discount, free_delivery=free_delivery)
