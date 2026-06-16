"""Sinov ma'lumotlari — `python -m app.seed`.

Idempotent: bo'sh bo'lsa to'ldiradi, bor bo'lsa tegmaydi. Toshkent tumanlari +
bir nechta namuna kategoriya/mahsulot. Bu 3-bosqichдаги admin paneldan oldin
botni sinab ko'rish uchun. Production'da kerak emas.
"""
import asyncio
from decimal import Decimal

from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.models import Category, District, Product

# Toshkent tumanlari + taxminiy yetkazib berish narxi (so'm)
DISTRICTS = [
    ("Bektemir", 30000),
    ("Chilonzor", 20000),
    ("Mirobod", 18000),
    ("Mirzo Ulug'bek", 20000),
    ("Olmazor", 22000),
    ("Sergeli", 28000),
    ("Shayxontohur", 18000),
    ("Uchtepa", 22000),
    ("Yakkasaroy", 18000),
    ("Yashnobod", 22000),
    ("Yangihayot", 28000),
    ("Yunusobod", 22000),
]

# Namuna katalog: kategoriya → mahsulotlar (nom, narx, tannarx, qoldiq)
CATALOG = {
    "Yuz parvarishi": [
        ("COSRX Snail Mucin essensiya", 145000, 90000, 30),
        ("Beauty of Joseon quyosh kremi SPF50", 120000, 75000, 25),
        ("Anua Heartleaf toner", 135000, 85000, 20),
    ],
    "Niqoblar": [
        ("Mediheal kollagen niqob (10 dona)", 95000, 55000, 40),
        ("Some By Mi mochi niqob", 70000, 40000, 35),
    ],
    "Lab va ko'z": [
        ("Rom&nd lab tinti", 85000, 50000, 50),
        ("Etude House qosh qalami", 45000, 25000, 60),
    ],
}


async def seed() -> None:
    async with SessionLocal() as session:
        # ─── Tumanlar ───
        count = await session.scalar(select(func.count()).select_from(District))
        if count == 0:
            session.add_all(
                District(name=name, delivery_fee=Decimal(fee)) for name, fee in DISTRICTS
            )
            print(f"+ {len(DISTRICTS)} ta tuman qo'shildi")
        else:
            print(f"= Tumanlar mavjud ({count} ta) — tegilmadi")

        # ─── Katalog ───
        cat_count = await session.scalar(select(func.count()).select_from(Category))
        if cat_count == 0:
            for cat_name, products in CATALOG.items():
                slug = cat_name.lower().replace(" ", "-").replace("'", "")
                category = Category(name=cat_name, slug=slug, is_active=True)
                session.add(category)
                await session.flush()  # category.id olish uchun
                for name, price, cost, stock in products:
                    session.add(
                        Product(
                            category_id=category.id,
                            name=name,
                            price=Decimal(price),
                            cost_price=Decimal(cost),
                            stock_qty=stock,
                            is_active=True,
                        )
                    )
            total = sum(len(v) for v in CATALOG.values())
            print(f"+ {len(CATALOG)} kategoriya, {total} mahsulot qo'shildi")
        else:
            print(f"= Katalog mavjud ({cat_count} kategoriya) — tegilmadi")

        await session.commit()
    print("✅ Seed tugadi")


if __name__ == "__main__":
    asyncio.run(seed())
