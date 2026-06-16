"""Katalog handlerlari: kategoriya → mahsulot → tafsilot → savatga qo'shish.

Mahsulot tafsiloti ikki xabardan iborat: albom (rasmlar, tugmasiz) +
boshqaruv xabari (matn + tugmalar). Telegram albomga tugma qo'shishga ruxsat
bermaydi. Navigatsiyada albom [[app/bot/album.py]] orqali tozalanadi.
"""
import os
from contextlib import suppress

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardMarkup,
    Message,
    URLInputFile,
)

from app.bot.album import clear_album, send_album
from app.bot.keyboards.catalog import (
    categories_kb,
    product_detail_kb,
    products_kb,
)
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.utils import format_money
from app.models import Product
from app.services import cart as cart_service
from app.services import catalog as catalog_service

router = Router(name="catalog")

CAPTION_LIMIT = 1024  # Telegram rasm caption chegarasi (matn xabari uchun emas)


def _photo_input(image_url: str) -> FSInputFile | URLInputFile | None:
    """image_url → aiogram rasm manbai.

    - http(s) bo'lsa: URL orqali (Telegram serveri yoki R2 dan yuklab oladi).
    - /media/... lokal yo'l bo'lsa: diskdan o'qiymiz (domen ochiq bo'lishi shart emas).
    """
    if image_url.startswith(("http://", "https://")):
        return URLInputFile(image_url)
    base = settings.media_url_base
    if image_url.startswith(base):
        rel = image_url[len(base):].lstrip("/")
        path = os.path.join(settings.media_root, rel)
        if os.path.exists(path):
            return FSInputFile(path)
    return None


def _product_caption(product: Product) -> str:
    """Mahsulot tafsiloti matni (boshqaruv xabari uchun)."""
    stock_line = (
        f"✅ Mavjud ({product.stock_qty} dona)"
        if product.stock_qty > 0
        else "⛔️ Hozircha tugagan"
    )
    return (
        f"<b>{product.name}</b>\n\n"
        f"{product.description or ''}\n\n"
        f"💵 Narxi: <b>{format_money(product.price)}</b>\n"
        f"{stock_line}"
    )


async def _render(call: CallbackQuery, text: str, kb: InlineKeyboardMarkup) -> None:
    """Matnli ro'yxat xabarini joyida yangilaydi; bo'lmasa qayta yuboradi."""
    try:
        await call.message.edit_text(text, reply_markup=kb)
    except TelegramBadRequest:
        with suppress(TelegramBadRequest):
            await call.message.delete()
        await call.message.answer(text, reply_markup=kb)


async def _send_categories(message: Message) -> None:
    async with SessionLocal() as session:
        categories = await catalog_service.list_categories(session)
    if not categories:
        await message.answer("Hozircha kategoriyalar yo'q. Tez orada qo'shamiz 🙌")
        return
    await message.answer("🛍 <b>Kategoriyalar</b> — tanlang:", reply_markup=categories_kb(categories))


@router.message(F.text == "🛍 Katalog")
async def open_catalog(message: Message, state: FSMContext) -> None:
    await clear_album(message.bot, message.chat.id, state)
    await _send_categories(message)


@router.callback_query(F.data == "cat:back")
async def back_to_categories(call: CallbackQuery, state: FSMContext) -> None:
    await clear_album(call.bot, call.message.chat.id, state)
    async with SessionLocal() as session:
        categories = await catalog_service.list_categories(session)
    await _render(call, "🛍 <b>Kategoriyalar</b> — tanlang:", categories_kb(categories))
    await call.answer()


@router.callback_query(F.data.startswith("cat:"))
async def show_category_products(call: CallbackQuery, state: FSMContext) -> None:
    category_id = int(call.data.split(":")[1])
    async with SessionLocal() as session:
        category = await catalog_service.get_category(session, category_id)
        products = await catalog_service.list_products(session, category_id=category_id)
    if not products:
        await call.answer("Bu kategoriyada mahsulot yo'q", show_alert=True)
        return
    await clear_album(call.bot, call.message.chat.id, state)
    title = category.name if category else "Mahsulotlar"
    await _render(call, f"📦 <b>{title}</b> — mahsulotni tanlang:", products_kb(products))
    await call.answer()


@router.callback_query(F.data.startswith("prod:"))
async def show_product(call: CallbackQuery, state: FSMContext) -> None:
    product_id = int(call.data.split(":")[1])
    async with SessionLocal() as session:
        product = await catalog_service.get_product(session, product_id)
    if product is None or not product.is_active:
        await call.answer("Mahsulot topilmadi", show_alert=True)
        return

    caption = _product_caption(product)
    kb = product_detail_kb(product)
    photos = [p for url in product.images if (p := _photo_input(url)) is not None]

    chat_id = call.message.chat.id
    # Eski ko'rinishni tozalaymiz: oldingi albom + joriy ro'yxat/karta xabari
    await clear_album(call.bot, chat_id, state)
    with suppress(TelegramBadRequest):
        await call.message.delete()

    # Albom (rasmlar) → keyin boshqaruv xabari (matn + tugmalar) ostida chiqadi
    await send_album(call.bot, chat_id, photos, state)
    await call.bot.send_message(chat_id, caption, reply_markup=kb)
    await call.answer()


@router.callback_query(F.data.startswith("add:"))
async def add_to_cart(call: CallbackQuery) -> None:
    product_id = int(call.data.split(":")[1])
    async with SessionLocal() as session:
        product = await catalog_service.get_product(session, product_id)
    if product is None or product.stock_qty <= 0:
        await call.answer("Mahsulot mavjud emas", show_alert=True)
        return
    await cart_service.add_item(call.from_user.id, product_id, 1)
    total = await cart_service.count(call.from_user.id)
    await call.answer(f"✅ Savatga qo'shildi (jami: {total} dona)")


@router.callback_query(F.data == "noop")
async def noop(call: CallbackQuery) -> None:
    await call.answer()
