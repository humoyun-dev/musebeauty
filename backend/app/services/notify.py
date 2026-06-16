"""Bildirishnoma servisi — admin va mijozga Telegram orqali xabar.

api va bot ALOHIDA jarayonlar. Shuning uchun bu servis aiogram Bot nusxasiga
bog'lanmaydi — to'g'ridan-to'g'ri Telegram HTTP API'ga httpx bilan murojaat qiladi.
Shunday qilib ham bot, ham api jarayonidan ishlatish mumkin.
"""
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger("notify")

_API = "https://api.telegram.org"


async def _send(chat_id: int, text: str) -> bool:
    if not settings.bot_token:
        logger.warning("BOT_TOKEN yo'q — bildirishnoma yuborilmadi")
        return False
    url = f"{_API}/bot{settings.bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code != 200:
                logger.warning("Telegram xato %s: %s", resp.status_code, resp.text)
                return False
            return True
    except httpx.HTTPError as exc:
        logger.warning("Bildirishnoma yuborilmadi: %s", exc)
        return False


async def notify_customer(telegram_id: int, text: str) -> bool:
    """Bitta mijozga xabar."""
    return await _send(telegram_id, text)


async def notify_admins(text: str) -> int:
    """Barcha adminlarga (.env ADMIN_TELEGRAM_IDS). Nechta yuborilganini qaytaradi."""
    sent = 0
    for admin_id in settings.admin_ids:
        if await _send(admin_id, text):
            sent += 1
    return sent
