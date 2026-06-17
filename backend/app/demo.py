"""To'liq demo dataset — `python -m app.demo`.

Ko'rsatish/sinov uchun BOY ma'lumot: real K-beauty katalog, demo admin,
chegirma + promokodlar, mijozlar va turli holatdagi buyurtmalar (admin dashboard
va hisobotlar jonli ko'rinishi uchun). Idempotent: har bo'lim bo'sh bo'lsa to'ldiradi.

PRODUCTION'da ishlatilmaydi — minimal bootstrap uchun `app.seed` bor.
"""
import asyncio
from decimal import Decimal

from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.models import (
    Category,
    Customer,
    Discount,
    District,
    Order,
    PaymeTransaction,  # noqa: F401  (metadata to'liq bo'lishi uchun)
    Product,
    Payment,  # noqa: F401  (metadata to'liq bo'lishi uchun)
    PromoCode,
)
from app.services import admin as admin_service
from app.services import order as order_service
from app.services import payment as payment_service

# ───────────────────────── Tumanlar ─────────────────────────
DISTRICTS = [
    ("Bektemir", 30000), ("Chilonzor", 20000), ("Mirobod", 18000),
    ("Mirzo Ulug'bek", 20000), ("Olmazor", 22000), ("Sergeli", 28000),
    ("Shayxontohur", 18000), ("Uchtepa", 22000), ("Yakkasaroy", 18000),
    ("Yashnobod", 22000), ("Yangihayot", 28000), ("Yunusobod", 22000),
]

# ───────────────────────── Katalog ─────────────────────────
# (nom, narx, tannarx, qoldiq, tavsif)
CATALOG = {
    "Yuz parvarishi": [
        ("COSRX Advanced Snail 96 Mucin essensiya", 145000, 92000, 60, "Salyak ekstrakti bilan namlovchi va tiklovchi essensiya."),
        ("Beauty of Joseon Glow Serum (Propolis+Niacinamide)", 135000, 86000, 50, "Yorqinlik beruvchi propolis va niacinamide zardobi."),
        ("Anua Heartleaf 77% Soothing toner", 130000, 83000, 55, "Sezgir teri uchun tinchlantiruvchi toner."),
        ("Torriden Dive-In gialuron zardobi", 130000, 82000, 45, "5 xil gialuron kislotasi bilan chuqur namlik."),
        ("Numbuzin No.3 yorqinlik zardobi", 155000, 99000, 35, "Teri tonini tenglashtiruvchi vitaminli zardob."),
        ("Round Lab 1025 Dokdo toner", 120000, 76000, 50, "Dengiz suvi minerallari bilan namlovchi toner."),
        ("Isntree gialuron toner", 115000, 73000, 40, "Yengil, tez singuvchi namlovchi toner."),
        ("Mixsoon Bean essensiya", 110000, 70000, 40, "Loviya fermenti bilan yumshoq peeling va namlik."),
    ],
    "Tozalash": [
        ("COSRX Salicylic Acid yumshoq tozalagich", 95000, 60000, 50, "Toza teri uchun salisil kislotali gel tozalagich."),
        ("Anua Heartleaf tozalovchi moy", 140000, 89000, 45, "Makiyaj va SPF ni yumshoq eritadi."),
        ("Skin1004 Centella yengil tozalovchi moy", 135000, 86000, 40, "Sezgir teri uchun centella moyi."),
        ("Etude SoonJung pH 5.5 ko'pikli tozalagich", 85000, 54000, 55, "Kam ishqorli, teri to'sig'ini asraydi."),
    ],
    "Niqoblar": [
        ("Mediheal choy daraxti niqobi (10 dona)", 95000, 57000, 70, "Yog'li teri uchun tinchlantiruvchi to'plam."),
        ("Mediheal kollagen niqobi (10 dona)", 98000, 59000, 70, "Elastiklik beruvchi kollagen niqoblari."),
        ("Some By Mi Snail Truecica niqobi", 75000, 45000, 60, "Tiklovchi salyak va cica niqobi."),
        ("Innisfree vulqon loy niqobi", 90000, 56000, 45, "Teshiklarni tozalovchi loy niqobi."),
    ],
    "Quyoshdan himoya": [
        ("Beauty of Joseon Relief Sun SPF50+", 120000, 76000, 80, "Yengil, oqarmaydigan kunlik himoya."),
        ("Round Lab qayin sharbati SPF50+", 125000, 79000, 60, "Namlovchi, sezgir teriga mos."),
        ("Skin1004 Centella quyosh kremi", 130000, 82000, 50, "Tinchlantiruvchi centella SPF."),
    ],
    "Ko'z parvarishi": [
        ("COSRX Advanced Snail ko'z kremi", 125000, 80000, 40, "Ko'z atrofi uchun namlovchi krem."),
        ("Numbuzin ko'z patchlari (60 dona)", 140000, 89000, 35, "Shishni kamaytiruvchi gidrogel patchlar."),
    ],
    "Lab parvarishi": [
        ("Laneige Lip Sleeping Mask", 160000, 102000, 50, "Tungi namlovchi lab niqobi."),
        ("Rom&nd Glasting suvli yaltiroq", 78000, 47000, 65, "Yengil, yopishqoq bo'lmagan lab yaltirog'i."),
    ],
    "Makiyaj": [
        ("Rom&nd Juicy Lasting tint", 85000, 51000, 70, "Uzoq saqlanuvchi suvli lab bo'yog'i."),
        ("Rom&nd Better Than Eyes palitra", 145000, 92000, 30, "Kundalik 9 rangli ko'z soyalari."),
        ("Clio Kill Cover cushion", 165000, 105000, 35, "Yuqori qoplamali, bardoshli kushon."),
        ("Tirtir Mask Fit cushion", 175000, 112000, 30, "Yengil, tabiiy qoplamali kushon."),
    ],
    "To'plamlar": [
        ("MUSE Boshlang'ich to'plam (toner+serum+krem)", 320000, 205000, 25, "Yangi boshlovchilar uchun 3 bosqichli to'plam."),
        ("MUSE Yorqinlik to'plami", 290000, 185000, 20, "Yorqin teri uchun zardob + niqob to'plami."),
    ],
}

# ───────────────────────── Chegirmalar (auto) ─────────────────────────
DISCOUNTS = [
    {"name": "Bahor aksiyasi — barchaga 5%", "type": "percent", "value": Decimal("5"), "scope": "all"},
]

# ───────────────────────── Promokodlar ─────────────────────────
PROMOS = [
    {"code": "WELCOME10", "type": "percent", "value": Decimal("10"), "min_order_amount": Decimal("100000"), "first_order_only": True},
    {"code": "BAHOR2026", "type": "percent", "value": Decimal("15"), "max_discount": Decimal("50000"), "usage_limit": 100},
    {"code": "FREEDOST", "type": "free_delivery", "value": Decimal("0"), "min_order_amount": Decimal("200000")},
    {"code": "MINUS20K", "type": "fixed", "value": Decimal("20000"), "min_order_amount": Decimal("150000")},
]

# ───────────────────────── Mijozlar ─────────────────────────
# (telegram_id | None, ism, telefon)
CUSTOMERS = [
    (900000001, "Madina Karimova", "+998901112201"),
    (900000002, "Dilnoza Yusupova", "+998901112202"),
    (900000003, "Aziza Tohirova", "+998901112203"),
    (None, "Gulnora (web)", "+998901112204"),
    (None, "Sevara (web)", "+998901112205"),
    (900000006, "Kamola Saidova", "+998901112206"),
]

# ─── Buyurtmalar: (mijoz_idx, [(prod_idx, qty)], promokod, yakuniy_holat, kutilayotgan_chek) ───
# prod_idx — yaratilgan mahsulotlar ro'yxatidagi tartib (0 dan)
ORDERS = [
    (0, [(0, 1), (16, 1)], "WELCOME10", "yetkazildi", False),
    (1, [(2, 2)], None, "jonatildi", False),
    (2, [(28, 1)], "BAHOR2026", "tayyorlandi", False),
    (3, [(1, 1), (12, 1)], "FREEDOST", "tolandi", False),
    (4, [(23, 2), (24, 1)], None, "tolandi", False),
    (5, [(27, 1)], "MINUS20K", "yetkazildi", False),
    (0, [(4, 1)], None, "yangi", True),     # chek yuborilgan, kutilmoqda
    (1, [(20, 1), (21, 1)], None, "yangi", True),
    (2, [(8, 3)], None, "yangi", False),    # to'lanmagan
    (3, [(17, 1)], "BAHOR2026", "yetkazildi", False),
]


async def _seed_catalog(session) -> list[Product]:
    products: list[Product] = []
    img = 1
    for cat_name, items in CATALOG.items():
        slug = cat_name.lower().replace(" ", "-").replace("'", "")
        category = Category(name=cat_name, slug=slug, is_active=True)
        session.add(category)
        await session.flush()
        for name, price, cost, stock, desc in items:
            # Har mahsulotga 3 ta rasmli galereya ([0] = muqova) — albomni sinash uchun
            gallery = [f"https://picsum.photos/seed/muse{img}-{k}/500/500" for k in range(3)]
            p = Product(
                category_id=category.id, name=name, description=desc,
                image_url=gallery[0], gallery=gallery,
                price=Decimal(price), cost_price=Decimal(cost),
                stock_qty=stock, is_active=True,
            )
            session.add(p)
            products.append(p)
            img += 1
    await session.flush()
    return products


async def demo() -> None:
    async with SessionLocal() as session:
        # ─── Tumanlar ───
        if await session.scalar(select(func.count()).select_from(District)) == 0:
            session.add_all(District(name=n, delivery_fee=Decimal(f)) for n, f in DISTRICTS)
            print(f"+ {len(DISTRICTS)} tuman")

        # ─── Katalog ───
        if await session.scalar(select(func.count()).select_from(Category)) == 0:
            prods = await _seed_catalog(session)
            print(f"+ {len(CATALOG)} kategoriya, {len(prods)} mahsulot")
        else:
            print("= katalog mavjud — tegilmadi")

        # ─── Chegirmalar ───
        if await session.scalar(select(func.count()).select_from(Discount)) == 0:
            session.add_all(Discount(**d, is_active=True) for d in DISCOUNTS)
            print(f"+ {len(DISCOUNTS)} chegirma")

        # ─── Promokodlar ───
        if await session.scalar(select(func.count()).select_from(PromoCode)) == 0:
            session.add_all(PromoCode(**p, is_active=True) for p in PROMOS)
            print(f"+ {len(PROMOS)} promokod")

        await session.commit()

    # ─── Demo admin ───
    async with SessionLocal() as session:
        await admin_service.create_admin(
            session, username="admin", password="Admin12345", role="superadmin"
        )
    print("+ admin (admin / Admin12345)")

    # ─── Mijozlar + buyurtmalar ───
    async with SessionLocal() as session:
        has_orders = await session.scalar(select(func.count()).select_from(Order))
        if has_orders:
            print("= buyurtmalar mavjud — tegilmadi")
            await _summary(session)
            return

        # Mijozlar
        customers: list[Customer] = []
        for tg, name, phone in CUSTOMERS:
            c = Customer(telegram_id=tg, name=name, phone=phone)
            session.add(c)
            customers.append(c)
        await session.flush()

        # Mahsulotlar (tartib bo'yicha)
        products = (await session.execute(select(Product).order_by(Product.id))).scalars().all()
        districts = (await session.execute(select(District).order_by(District.id))).scalars().all()
        await session.commit()

    # Buyurtmalarni servis orqali yaratamiz (qoldiq/narx to'g'ri)
    created = 0
    for ci, lines, promo, final_status, pending in ORDERS:
        async with SessionLocal() as session:
            cust = (await session.execute(
                select(Customer).where(Customer.phone == CUSTOMERS[ci][2])
            )).scalar_one()
            items = {products[pi].id: qty for pi, qty in lines}
            district = districts[(ci + created) % len(districts)]
            try:
                order = await order_service.create_order_from_cart(
                    session, customer=cust, items=items,
                    district_id=district.id, address=f"{district.name}, ko'cha {created + 1}",
                    phone=cust.phone, promo_code=promo,
                )
            except Exception:  # promokod/qoldiq xatosi bo'lsa — rollback va kodsiz qayta
                await session.rollback()
                order = await order_service.create_order_from_cart(
                    session, customer=cust, items=items,
                    district_id=district.id, address=f"{district.name}, ko'cha {created + 1}",
                    phone=cust.phone, promo_code=None,
                )

            # Kutilayotgan chek
            if pending:
                await payment_service.submit_receipt(
                    session, order_id=order.id, amount=order.total, screenshot_url="demo_chek_file_id"
                )

            # Holatni oldinga suramiz (tolandi → ... → yakuniy)
            if final_status != "yangi":
                chain = ["tolandi", "tayyorlandi", "jonatildi", "yetkazildi"]
                target_idx = chain.index(final_status)
                for st in chain[: target_idx + 1]:
                    await order_service.set_status(session, order.id, st)
            created += 1

    async with SessionLocal() as session:
        print(f"+ {len(CUSTOMERS)} mijoz, {created} buyurtma")
        await _summary(session)


async def _summary(session) -> None:
    from app.services import report
    dash = await report.dashboard(session)
    print("\n📊 Dashboard:")
    print(f"   Bugungi buyurtma: {dash['today']['orders_count']}, daromad: {int(dash['today']['revenue'])}, foyda: {int(dash['today']['profit'])}")
    print(f"   Mijozlar: {dash['total_customers']}, faol mahsulot: {dash['active_products']}")
    print(f"   Kam qoldi: {dash['low_stock_count']}, kutilayotgan to'lov: {dash['pending_payments']}")
    tops = await report.top_products(session, limit=3)
    if tops:
        print("   Top: " + ", ".join(f"{t['name'][:20]}({t['qty_sold']})" for t in tops))
    print("\n✅ Demo data tayyor!")


if __name__ == "__main__":
    asyncio.run(demo())
