"""Katalog uchun inline klaviaturalar."""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.utils import format_money
from app.models import Category, Product


def categories_kb(categories: list[Category]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for cat in categories:
        kb.button(text=cat.name, callback_data=f"cat:{cat.id}")
    kb.adjust(2)
    return kb.as_markup()


def products_kb(products: list[Product]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for p in products:
        # Narx va qoldiq holatini tugmada ko'rsatamiz
        suffix = "" if p.stock_qty > 0 else " ⛔️"
        kb.button(
            text=f"{p.name} — {format_money(p.price)}{suffix}",
            callback_data=f"prod:{p.id}",
        )
    kb.button(text="⬅️ Kategoriyalar", callback_data="cat:back")
    kb.adjust(1)
    return kb.as_markup()


def product_detail_kb(product: Product) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if product.stock_qty > 0:
        kb.button(text="➕ Savatga qo'shish", callback_data=f"add:{product.id}")
    kb.button(text="🛒 Savat", callback_data="cart:open")
    if product.category_id:
        kb.button(text="⬅️ Orqaga", callback_data=f"cat:{product.category_id}")
    else:
        kb.button(text="⬅️ Kategoriyalar", callback_data="cat:back")
    kb.adjust(1)
    return kb.as_markup()
