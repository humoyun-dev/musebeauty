"""Savat handlerlari: ko'rish, miqdor o'zgartirish, o'chirish, tozalash."""
from contextlib import suppress

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.album import clear_album
from app.bot.keyboards.cart import cart_kb
from app.core.database import SessionLocal
from app.core.utils import format_money
from app.services import cart as cart_service
from app.services import catalog as catalog_service

router = Router(name="cart")


async def _render(owner: int) -> tuple[str, object | None]:
    """Savat matni va klaviaturasini tayyorlaydi."""
    items = await cart_service.get_items(owner)
    if not items:
        return "🛒 Savatingiz bo'sh.\n\n«🛍 Katalog» orqali mahsulot tanlang.", None

    products = {}
    subtotal = 0
    lines = []
    async with SessionLocal() as session:
        for pid, qty in items.items():
            product = await catalog_service.get_product(session, pid)
            if product is None:
                # Mahsulot o'chirilgan bo'lsa savatdan ham olib tashlaymiz
                await cart_service.remove_item(owner, pid)
                continue
            products[pid] = product
            line_total = product.price * qty
            subtotal += line_total
            lines.append(f"• {product.name} — {qty} × {format_money(product.price)} = {format_money(line_total)}")

    # O'chirilgan mahsulotlardan keyin yangilangan ro'yxat
    items = await cart_service.get_items(owner)
    if not items:
        return "🛒 Savatingiz bo'sh.", None

    text = (
        "🛒 <b>Savat</b>\n\n"
        + "\n".join(lines)
        + f"\n\n<b>Jami: {format_money(subtotal)}</b>\n"
        "<i>(yetkazib berish keyingi bosqichda qo'shiladi)</i>"
    )
    return text, cart_kb(products, items)


@router.message(F.text == "🛒 Savat")
async def open_cart_message(message: Message, state: FSMContext) -> None:
    await clear_album(message.bot, message.chat.id, state)
    text, kb = await _render(message.from_user.id)
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "cart:open")
async def open_cart_call(call: CallbackQuery, state: FSMContext) -> None:
    # Mahsulot albomi + boshqaruv kartasini tozalab, savatni yangidan yuboramiz
    await clear_album(call.bot, call.message.chat.id, state)
    with suppress(TelegramBadRequest):
        await call.message.delete()
    text, kb = await _render(call.from_user.id)
    await call.message.answer(text, reply_markup=kb)
    await call.answer()


async def _refresh(call: CallbackQuery) -> None:
    text, kb = await _render(call.from_user.id)
    try:
        await call.message.edit_text(text, reply_markup=kb)
    except Exception:
        # Matn o'zgarmasa Telegram xato beradi — e'tibor bermaymiz
        pass


@router.callback_query(F.data.startswith("cinc:"))
async def inc(call: CallbackQuery) -> None:
    pid = int(call.data.split(":")[1])
    # Qoldiqdan oshmaslik uchun tekshiramiz
    async with SessionLocal() as session:
        product = await catalog_service.get_product(session, pid)
    current = (await cart_service.get_items(call.from_user.id)).get(pid, 0)
    if product and current >= product.stock_qty:
        await call.answer("Qoldiq yetarli emas", show_alert=True)
        return
    await cart_service.add_item(call.from_user.id, pid, 1)
    await _refresh(call)
    await call.answer()


@router.callback_query(F.data.startswith("cdec:"))
async def dec(call: CallbackQuery) -> None:
    pid = int(call.data.split(":")[1])
    await cart_service.add_item(call.from_user.id, pid, -1)
    await _refresh(call)
    await call.answer()


@router.callback_query(F.data.startswith("cdel:"))
async def delete(call: CallbackQuery) -> None:
    pid = int(call.data.split(":")[1])
    await cart_service.remove_item(call.from_user.id, pid)
    await _refresh(call)
    await call.answer("O'chirildi")


@router.callback_query(F.data == "cart:clear")
async def clear(call: CallbackQuery) -> None:
    await cart_service.clear(call.from_user.id)
    await _refresh(call)
    await call.answer("Savat tozalandi")
