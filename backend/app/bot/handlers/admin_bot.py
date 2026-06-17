"""Admin bot — faqat adminlar (ADMIN_TELEGRAM_IDS) uchun.

Adminlar mijoz (e-commerce) oqimini ko'rmaydi. Telegram orqali boshqaruv:
buyurtmalar + holat, to'lov cheklarini tasdiqlash, kam qoldi, kunlik hisobot.
"""
from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards.admin import (
    STATUS_LABEL,
    admin_menu_kb,
    order_status_kb,
    payment_confirm_kb,
)
from app.core.database import SessionLocal
from app.core.utils import format_money
from app.models import Customer, Order
from app.services import location as location_service
from app.services import order as order_service
from app.services import payment as payment_service
from app.services import report as report_service
from app.services.order import InvalidStatusTransition

router = Router(name="admin_bot")


async def _customer_tg(session, customer_id: int) -> int | None:
    cust = await session.get(Customer, customer_id)
    return cust.telegram_id if cust else None


@router.message(CommandStart())
async def admin_start(message: Message) -> None:
    await message.answer(
        "👮 <b>MUSE BEAUTY — Admin panel</b>\n\n"
        "Bu yerda buyurtmalarni boshqarasiz, to'lovlarni tasdiqlaysiz va hisobot ko'rasiz.\n"
        "To'liq boshqaruv — admin saytida (brauzer).",
        reply_markup=admin_menu_kb(),
    )


# ─────────────────────────── Buyurtmalar ───────────────────────────
def _order_text(o: Order) -> str:
    map_line = ""
    if o.latitude is not None and o.longitude is not None:
        g = location_service.google_link(o.latitude, o.longitude)
        y = location_service.yandex_link(o.latitude, o.longitude)
        map_line = f"🗺 <a href='{g}'>Google</a> | <a href='{y}'>Yandex</a>\n"
    return (
        f"🧾 <b>Buyurtma #{o.id}</b>\n"
        f"👤 {o.phone or '-'}\n"
        f"💵 {format_money(o.total)}\n"
        f"📍 {o.address or '-'}\n"
        f"{map_line}"
        f"Holat: <b>{STATUS_LABEL.get(o.status, o.status)}</b>"
    )


@router.message(F.text == "🆕 Buyurtmalar")
async def admin_orders(message: Message) -> None:
    async with SessionLocal() as session:
        orders = await order_service.list_orders(session, limit=8)
    if not orders:
        await message.answer("Hozircha buyurtma yo'q.")
        return
    await message.answer(f"Oxirgi {len(orders)} ta buyurtma:")
    for o in orders:
        await message.answer(_order_text(o), reply_markup=order_status_kb(o))


@router.callback_query(F.data.startswith("oadm:set:"))
async def admin_set_status(call: CallbackQuery) -> None:
    _, _, oid_s, status = call.data.split(":")
    oid = int(oid_s)
    async with SessionLocal() as session:
        try:
            order = await order_service.set_status(session, oid, status)
        except InvalidStatusTransition as exc:
            await call.answer(str(exc), show_alert=True)
            return
        except ValueError:
            await call.answer("Buyurtma topilmadi", show_alert=True)
            return
        tg = await _customer_tg(session, order.customer_id)

    await call.message.edit_text(_order_text(order), reply_markup=order_status_kb(order))
    await call.answer(f"Holat: {STATUS_LABEL.get(status, status)}")

    # Mijozga xabar (Telegram mijozi bo'lsa)
    if tg:
        try:
            await call.bot.send_message(
                tg, f"📦 Buyurtmangiz #{order.id} holati: <b>{STATUS_LABEL.get(status, status)}</b>"
            )
        except Exception:
            pass


# ─────────────────────────── To'lovlar ───────────────────────────
@router.message(F.text == "💳 To'lovlar")
async def admin_payments(message: Message) -> None:
    async with SessionLocal() as session:
        pending = await payment_service.list_payments(session, only_pending=True, limit=10)
    if not pending:
        await message.answer("✅ Tasdiqlanmagan to'lov yo'q.")
        return
    await message.answer(f"⏳ {len(pending)} ta tasdiqlanmagan to'lov:")
    for p in pending:
        caption = f"🧾 Buyurtma #{p.order_id}\n💵 {format_money(p.amount)}\nChekni tekshiring va tasdiqlang."
        # Chek rasmi (mijoz yuborgan file_id). Yaroqsiz bo'lsa — matn.
        try:
            await message.answer_photo(p.screenshot_url, caption=caption, reply_markup=payment_confirm_kb(p.id))
        except Exception:
            await message.answer(caption + "\n(chek rasmi mavjud emas)", reply_markup=payment_confirm_kb(p.id))


@router.callback_query(F.data.startswith("padm:ok:"))
async def admin_confirm_payment(call: CallbackQuery) -> None:
    pid = int(call.data.split(":")[2])
    async with SessionLocal() as session:
        try:
            payment = await payment_service.confirm_payment(session, payment_id=pid, admin_id=None)
        except ValueError:
            await call.answer("To'lov topilmadi", show_alert=True)
            return
        order = await session.get(Order, payment.order_id)
        tg = await _customer_tg(session, order.customer_id) if order else None

    # Tugmani olib tashlab, tasdiqlangan deb belgilaymiz
    try:
        await call.message.edit_caption(
            caption=f"✅ <b>Tasdiqlandi</b> — Buyurtma #{payment.order_id} to'landi",
            reply_markup=None,
        )
    except Exception:
        try:
            await call.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
    await call.answer("To'lov tasdiqlandi ✅")

    if tg:
        try:
            await call.bot.send_message(
                tg, f"✅ To'lovingiz qabul qilindi! Buyurtma #{payment.order_id} tayyorlanmoqda 💖"
            )
        except Exception:
            pass


# ─────────────────────────── Kam qoldi ───────────────────────────
@router.message(F.text == "⚠️ Kam qoldi")
async def admin_low_stock(message: Message) -> None:
    async with SessionLocal() as session:
        products = await report_service.low_stock_products(session, threshold=5)
    if not products:
        await message.answer("✅ Hamma mahsulot yetarli (5+ dona).")
        return
    lines = "\n".join(f"• {p.name}: <b>{p.stock_qty}</b> dona" for p in products)
    await message.answer(f"⚠️ <b>Kam qolgan mahsulotlar</b>:\n\n{lines}")


# ─────────────────────────── Hisobot ───────────────────────────
@router.message(F.text == "📊 Hisobot")
async def admin_report(message: Message) -> None:
    async with SessionLocal() as session:
        d = await report_service.dashboard(session)
        tops = await report_service.top_products(session, limit=5, days=30)
    top_lines = "\n".join(f"  {i + 1}. {t['name']} — {t['qty_sold']} dona" for i, t in enumerate(tops))
    await message.answer(
        f"📊 <b>Hisobot ({d['today']['date']})</b>\n\n"
        f"<b>Bugun</b>\n"
        f"  Buyurtma: {d['today']['orders_count']} ta\n"
        f"  Daromad: {format_money(d['today']['revenue'])}\n"
        f"  Foyda: {format_money(d['today']['profit'])}\n\n"
        f"<b>Bu oy</b>\n"
        f"  Daromad: {format_money(d['month']['revenue'])}\n"
        f"  Foyda: {format_money(d['month']['profit'])}\n\n"
        f"Mijozlar: {d['total_customers']} · Faol mahsulot: {d['active_products']}\n"
        f"Kam qoldi: {d['low_stock_count']} · Kutilayotgan to'lov: {d['pending_payments']}\n"
        + (f"\n🔥 <b>Top (30 kun)</b>:\n{top_lines}" if top_lines else "")
    )


# Adminlar uchun boshqa har qanday matn — menyuga yo'naltirish
@router.message(F.text)
async def admin_fallback(message: Message) -> None:
    await message.answer("Quyidagi menyudan tanlang 👇", reply_markup=admin_menu_kb())
