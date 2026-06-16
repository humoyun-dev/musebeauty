"""Admin bot klaviaturalari (faqat adminlar uchun)."""
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from app.models import Order
from app.services import order as order_service

# Holat kodi → tugma yorlig'i
STATUS_LABEL = {
    "yangi": "🆕 Yangi",
    "tolandi": "💰 To'landi",
    "tayyorlandi": "📦 Tayyorlandi",
    "jonatildi": "🚚 Jo'natildi",
    "yetkazildi": "✅ Yetkazildi",
    "bekor_qilindi": "❌ Bekor",
    "qaytarildi": "↩️ Qaytarildi",
}


def admin_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🆕 Buyurtmalar"), KeyboardButton(text="💳 To'lovlar")],
            [KeyboardButton(text="⚠️ Kam qoldi"), KeyboardButton(text="📊 Hisobot")],
        ],
        resize_keyboard=True,
    )


def order_status_kb(order: Order) -> InlineKeyboardMarkup | None:
    """Joriy holatdan keyingi ruxsat etilgan holatlar uchun tugmalar."""
    nexts = order_service.allowed_next(order.status)
    if not nexts:
        return None
    rows = [
        [InlineKeyboardButton(text=STATUS_LABEL.get(s, s), callback_data=f"oadm:set:{order.id}:{s}")]
        for s in nexts
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def payment_confirm_kb(payment_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ To'lovni tasdiqlash", callback_data=f"padm:ok:{payment_id}")]
        ]
    )
