"""Marketing CRUD — discounts (kodsiz) va promo_codes (kodli) boshqaruvi (admin).

Validatsiya/qo'llash mantiqi pricing.py va promo.py da; bu yerda faqat CRUD.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Discount, PromoCode


# ─────────────────────────── Discounts ───────────────────────────
async def list_discounts(session: AsyncSession, *, limit: int = 100) -> list[Discount]:
    stmt = select(Discount).order_by(Discount.id.desc()).limit(limit)
    return list((await session.execute(stmt)).scalars().all())


async def create_discount(session: AsyncSession, data: dict) -> Discount:
    obj = Discount(**data)
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def update_discount(session: AsyncSession, discount_id: int, data: dict) -> Discount | None:
    obj = await session.get(Discount, discount_id)
    if obj is None:
        return None
    for k, v in data.items():
        setattr(obj, k, v)
    await session.commit()
    await session.refresh(obj)
    return obj


async def delete_discount(session: AsyncSession, discount_id: int) -> bool:
    obj = await session.get(Discount, discount_id)
    if obj is None:
        return False
    await session.delete(obj)
    await session.commit()
    return True


# ─────────────────────────── Promo codes ───────────────────────────
async def list_promos(session: AsyncSession, *, limit: int = 100) -> list[PromoCode]:
    stmt = select(PromoCode).order_by(PromoCode.id.desc()).limit(limit)
    return list((await session.execute(stmt)).scalars().all())


async def create_promo(session: AsyncSession, data: dict) -> PromoCode:
    obj = PromoCode(**data)
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def update_promo(session: AsyncSession, promo_id: int, data: dict) -> PromoCode | None:
    obj = await session.get(PromoCode, promo_id)
    if obj is None:
        return None
    for k, v in data.items():
        setattr(obj, k, v)
    await session.commit()
    await session.refresh(obj)
    return obj


async def delete_promo(session: AsyncSession, promo_id: int) -> bool:
    obj = await session.get(PromoCode, promo_id)
    if obj is None:
        return False
    await session.delete(obj)
    await session.commit()
    return True
