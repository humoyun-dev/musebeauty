"""Bot filtrlari — admin va mijozni ajratish.

Admin Telegram ID'lari .env (ADMIN_TELEGRAM_IDS) da. Adminlar mijoz (e-commerce)
oqimini KO'RMAYDI — ularga admin bot ishlaydi.
"""
from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from app.core.config import settings


class IsAdmin(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        user = event.from_user
        return bool(user) and user.id in settings.admin_ids


class IsNotAdmin(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        user = event.from_user
        return not (bool(user) and user.id in settings.admin_ids)
