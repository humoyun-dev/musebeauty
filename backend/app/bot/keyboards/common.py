"""Umumiy klaviaturalar (reply va inline tugmalar)."""
from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def phone_request_kb() -> ReplyKeyboardMarkup:
    """Telefon raqamini bir tugma bilan ulashish (ro'yxatdan o'tish)."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Telefon raqamni ulashish", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def location_request_kb() -> ReplyKeyboardMarkup:
    """Aniq joylashuvni bir tugma bilan yuborish (checkout manzil bosqichi)."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Joylashuvni yuborish", request_location=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def main_menu_kb() -> ReplyKeyboardMarkup:
    """Asosiy menyu. 2-bosqichda katalog/savat to'liq ulanadi."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍 Katalog"), KeyboardButton(text="🛒 Savat")],
            [KeyboardButton(text="🎁 Aksiyalar"), KeyboardButton(text="📦 Buyurtmalarim")],
            [KeyboardButton(text="☎️ Aloqa")],
        ],
        resize_keyboard=True,
    )
