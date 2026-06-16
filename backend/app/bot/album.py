"""Mahsulot albomi (media group) xabarlarini kuzatish va tozalash.

Telegram albomga inline tugma biriktirib bo'lmaydi — shuning uchun mahsulot
tafsiloti = albom (faqat rasmlar) + alohida boshqaruv xabari (matn + tugmalar).
Navigatsiyada (orqaga / boshqa mahsulot / savat) albom xabarlarini o'chirish
kerak, shuning uchun ularning id'larini FSM (Redis) da saqlaymiz.
"""
from contextlib import suppress

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, InputMediaPhoto, URLInputFile

_KEY = "album_ids"
MAX_PHOTOS = 10  # Telegram media group limiti

PhotoInput = FSInputFile | URLInputFile


async def send_album(
    bot: Bot, chat_id: int, photos: list[PhotoInput], state: FSMContext
) -> None:
    """Rasmlarni albom qilib yuboradi va id'larini eslab qoladi.

    - 0 rasm → hech narsa yuborilmaydi.
    - 1 rasm → oddiy foto (media group min 2 ta talab qiladi).
    - 2..10 → media group.
    Rasm yuklab bo'lmasa — jim o'tadi (boshqaruv xabari baribir chiqadi).
    """
    photos = photos[:MAX_PHOTOS]
    ids: list[int] = []
    try:
        if len(photos) == 1:
            msg = await bot.send_photo(chat_id, photos[0])
            ids = [msg.message_id]
        elif len(photos) >= 2:
            media = [InputMediaPhoto(media=p) for p in photos]
            msgs = await bot.send_media_group(chat_id, media)
            ids = [m.message_id for m in msgs]
    except TelegramBadRequest:
        ids = []
    await state.update_data(**{_KEY: ids})


async def clear_album(bot: Bot, chat_id: int, state: FSMContext) -> None:
    """Avval ko'rsatilgan albom xabarlarini o'chiradi (bo'lsa)."""
    data = await state.get_data()
    ids = data.get(_KEY) or []
    if not ids:
        return
    for mid in ids:
        with suppress(TelegramBadRequest):
            await bot.delete_message(chat_id, mid)
    await state.update_data(**{_KEY: []})
