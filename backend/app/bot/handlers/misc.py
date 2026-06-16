"""Qo'shimcha menyu handlerlari: buyurtmalarim, aloqa."""
from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.utils import format_money
from app.models import Customer
from app.services import order as order_service
from app.services import pricing as pricing_service
from app.services import promo as promo_service
from app.models import PromoType

router = Router(name="misc")

# Holat kodini o'qishga qulay matnga
_STATUS_LABEL = {
    "yangi": "🆕 Yangi",
    "tolandi": "💰 To'landi",
    "tayyorlandi": "📦 Tayyorlandi",
    "jonatildi": "🚚 Jo'natildi",
    "yetkazildi": "✅ Yetkazildi",
    "bekor_qilindi": "❌ Bekor qilindi",
    "qaytarildi": "↩️ Qaytarildi",
}


@router.message(F.text == "📦 Buyurtmalarim")
async def my_orders(message: Message) -> None:
    async with SessionLocal() as session:
        customer = (
            await session.execute(
                select(Customer).where(Customer.telegram_id == message.from_user.id)
            )
        ).scalar_one_or_none()
        if customer is None:
            await message.answer("Avval /start orqali ro'yxatdan o'ting.")
            return
        orders = await order_service.list_customer_orders(session, customer.id)

    if not orders:
        await message.answer("Sizda hali buyurtma yo'q. «🛍 Katalog» dan boshlang!")
        return

    lines = [
        f"#{o.id} — {format_money(o.total)} — {_STATUS_LABEL.get(o.status, o.status)}"
        for o in orders
    ]
    await message.answer("📦 <b>Buyurtmalaringiz</b>\n\n" + "\n".join(lines))


def _discount_text(d) -> str:
    val = f"{int(d.value)}%" if d.type == "percent" else format_money(d.value)
    scope = {"all": "barchaga", "category": "kategoriyaga", "product": "mahsulotga"}.get(d.scope, "")
    return f"• <b>{d.name}</b> — {val} ({scope})"


def _promo_text(p) -> str:
    if p.type == PromoType.FREE_DELIVERY.value:
        body = "bepul yetkazib berish 🚚"
    else:
        body = f"{int(p.value)}%" if p.type == PromoType.PERCENT.value else format_money(p.value)
        body += " chegirma"
    extra = []
    if p.min_order_amount and int(p.min_order_amount) > 0:
        extra.append(f"{format_money(p.min_order_amount)} dan")
    if p.first_order_only:
        extra.append("birinchi buyurtma")
    suffix = f" · {' · '.join(extra)}" if extra else ""
    return f"🎟 <code>{p.code}</code> — {body}{suffix}"


@router.message(F.text == "🎁 Aksiyalar")
async def promotions(message: Message) -> None:
    async with SessionLocal() as session:
        discounts = await pricing_service.list_active_discounts(session)
        promos = await promo_service.list_active_promos(session)

    if not discounts and not promos:
        await message.answer("Hozircha faol aksiya yo'q. Tez orada qaytib keling 🌸")
        return

    parts = ["🎁 <b>Aksiyalar</b>\n"]
    if discounts:
        parts.append("<b>Chegirmalar</b> (avtomatik qo'llanadi):")
        parts += [_discount_text(d) for d in discounts]
        parts.append("")
    if promos:
        parts.append("<b>Promokodlar</b> (checkout'da kiriting):")
        parts += [_promo_text(p) for p in promos]
        parts.append("\n<i>Faqat bittasi qo'llanadi — eng foydalisi.</i>")

    await message.answer("\n".join(parts))


@router.message(F.text == "☎️ Aloqa")
async def contact(message: Message) -> None:
    await message.answer(
        "☎️ <b>Aloqa</b>\n\n"
        "Savol yoki muammo bo'lsa, shu yerga yozing — operatorlar javob beradi.\n"
        "Ish vaqti: 9:00–21:00"
    )
