"""Bot kirish nuqtasi — `python -m app.bot` shu faylni ishga tushiradi.

Long polling (webhook emas) — SSL shart emas, sozlash sodda (arxitektura §11).
FSM holatlari Redis'da saqlanadi.
"""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from app.bot.filters import IsAdmin, IsNotAdmin
from app.bot.handlers import admin_bot, cart, catalog, checkout, misc, payment, start
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot")


def build_dispatcher() -> Dispatcher:
    # FSM va savat Redis'da — tez, sessiyaga bog'liq, restartda yo'qolmaydi.
    storage = RedisStorage.from_url(settings.redis_url)
    dp = Dispatcher(storage=storage)

    # ─── Admin bot — FAQAT adminlar (ADMIN_TELEGRAM_IDS). Birinchi ulanadi. ───
    admin_bot.router.message.filter(IsAdmin())
    admin_bot.router.callback_query.filter(IsAdmin())
    dp.include_router(admin_bot.router)

    # ─── Mijoz oqimi (e-commerce) — adminlardan TASHQARI hammaga ───
    # Adminlar bu routerlarni ko'rmaydi (IsNotAdmin filtri).
    customer_routers = [
        start.router, catalog.router, cart.router,
        checkout.router, payment.router, misc.router,
    ]
    for r in customer_routers:
        r.message.filter(IsNotAdmin())
        r.callback_query.filter(IsNotAdmin())
        dp.include_router(r)
    return dp


async def main() -> None:
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN .env da ko'rsatilmagan")

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = build_dispatcher()

    # Eski navbatdagi update'larni tashlab, toza polling boshlaymiz
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot polling boshlandi")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
