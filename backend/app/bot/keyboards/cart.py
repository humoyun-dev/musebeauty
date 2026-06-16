"""Savat va checkout uchun inline klaviaturalar."""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.models import District, Product


def cart_kb(products: dict[int, Product], items: dict[int, int]) -> InlineKeyboardMarkup:
    """Har mahsulot uchun −/miqdor/+ va o'chirish; pastda tozalash + checkout."""
    kb = InlineKeyboardBuilder()
    for pid, qty in items.items():
        name = products[pid].name if pid in products else f"#{pid}"
        # Qator 1: mahsulot nomi (bosilmaydigan, faqat ko'rsatkich)
        kb.row(InlineKeyboardButton(text=f"{name[:28]} ×{qty}", callback_data="noop"))
        # Qator 2: − {qty} + 🗑
        kb.row(
            InlineKeyboardButton(text="➖", callback_data=f"cdec:{pid}"),
            InlineKeyboardButton(text=str(qty), callback_data="noop"),
            InlineKeyboardButton(text="➕", callback_data=f"cinc:{pid}"),
            InlineKeyboardButton(text="🗑", callback_data=f"cdel:{pid}"),
        )
    if items:
        kb.row(
            InlineKeyboardButton(text="🧹 Tozalash", callback_data="cart:clear"),
            InlineKeyboardButton(text="✅ Buyurtma berish", callback_data="checkout"),
        )
    return kb.as_markup()


def districts_kb(districts: list[District]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for d in districts:
        kb.button(text=d.name, callback_data=f"dist:{d.id}")
    kb.button(text="❌ Bekor qilish", callback_data="checkout:cancel")
    kb.adjust(2)
    return kb.as_markup()


def confirm_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Tasdiqlash", callback_data="checkout:confirm")
    kb.button(text="❌ Bekor qilish", callback_data="checkout:cancel")
    kb.adjust(1)
    return kb.as_markup()
