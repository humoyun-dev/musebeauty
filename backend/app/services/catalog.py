"""Katalog servisi — kategoriya/mahsulot o'qish, qidiruv, CRUD.

Bot, api/public va api/admin shu funksiyalarni chaqiradi (mantiq takrorlanmaydi).
O'qish — hammaga; yozish (CRUD) — faqat api/admin chaqiradi.
"""
import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category, Product


def slugify(text: str) -> str:
    """'Yuz parvarishi' → 'yuz-parvarishi' (kirill/maxsus belgilar tashlanadi)."""
    text = text.strip().lower().replace("'", "").replace("ʻ", "")
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s-]+", "-", text).strip("-")
    return text or "kategoriya"


async def list_categories(session: AsyncSession, *, only_active: bool = True) -> list[Category]:
    stmt = select(Category).order_by(Category.name)
    if only_active:
        stmt = stmt.where(Category.is_active.is_(True))
    return list((await session.execute(stmt)).scalars().all())


async def get_category(session: AsyncSession, category_id: int) -> Category | None:
    return await session.get(Category, category_id)


async def list_products(
    session: AsyncSession,
    *,
    category_id: int | None = None,
    only_active: bool = True,
    only_in_stock: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> list[Product]:
    stmt = select(Product).order_by(Product.name)
    if category_id is not None:
        stmt = stmt.where(Product.category_id == category_id)
    if only_active:
        stmt = stmt.where(Product.is_active.is_(True))
    if only_in_stock:
        stmt = stmt.where(Product.stock_qty > 0)
    stmt = stmt.limit(limit).offset(offset)
    return list((await session.execute(stmt)).scalars().all())


async def get_product(session: AsyncSession, product_id: int) -> Product | None:
    return await session.get(Product, product_id)


async def search_products(
    session: AsyncSession, query: str, *, limit: int = 30
) -> list[Product]:
    pattern = f"%{query.strip()}%"
    stmt = (
        select(Product)
        .where(Product.is_active.is_(True), Product.name.ilike(pattern))
        .order_by(Product.name)
        .limit(limit)
    )
    return list((await session.execute(stmt)).scalars().all())


# ─────────────────────── Yozish (CRUD) — faqat admin ───────────────────────
async def create_category(session: AsyncSession, data: dict) -> Category:
    if not data.get("slug"):
        data["slug"] = slugify(data["name"])
    category = Category(**data)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


async def update_category(session: AsyncSession, category_id: int, data: dict) -> Category | None:
    category = await session.get(Category, category_id)
    if category is None:
        return None
    for key, value in data.items():
        setattr(category, key, value)
    await session.commit()
    await session.refresh(category)
    return category


def _sync_cover(data: dict) -> None:
    """gallery va image_url ni moslashtiradi: muqova doim gallery[0].

    - gallery berilsa → image_url = gallery[0] (bo'sh bo'lsa None).
    - faqat image_url berilsa (eski yo'l) → gallery = [image_url].
    """
    if "gallery" in data:
        gallery = data.get("gallery") or []
        data["gallery"] = gallery
        data["image_url"] = gallery[0] if gallery else None
    elif data.get("image_url"):
        data["gallery"] = [data["image_url"]]


async def create_product(session: AsyncSession, data: dict) -> Product:
    _sync_cover(data)
    product = Product(**data)
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


async def update_product(session: AsyncSession, product_id: int, data: dict) -> Product | None:
    product = await session.get(Product, product_id)
    if product is None:
        return None
    _sync_cover(data)
    for key, value in data.items():
        setattr(product, key, value)
    await session.commit()
    await session.refresh(product)
    return product


async def delete_product(session: AsyncSession, product_id: int) -> bool:
    """Yumshoq o'chirish — is_active=False (buyurtma tarixini buzmaslik uchun)."""
    product = await session.get(Product, product_id)
    if product is None:
        return False
    product.is_active = False
    await session.commit()
    return True
