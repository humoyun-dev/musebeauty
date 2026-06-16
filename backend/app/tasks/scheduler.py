"""Rejalashtirilgan ishlar (APScheduler) — api jarayonida ishlaydi (1 nusxa).

Ishlar:
  • expire_promos  — muddati tugagan promokodlarni o'chiradi (har soat)
  • low_stock_alert — kam qolgan mahsulotlar haqida adminlarga (har kuni 09:00)
  • daily_report   — kunlik savdo/foyda adminlarga (har kuni 21:00)
"""
import logging
from datetime import datetime, timedelta, timezone

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select, update

from app.core.database import SessionLocal
from app.core.utils import format_money
from app.models import Order, OrderStatus, PaymentStatus, PromoCode
from app.services import notify as notify_service
from app.services import order as order_service
from app.services import report as report_service

# To'lanmagan buyurtma necha soatdan keyin avtomatik bekor bo'ladi
STALE_ORDER_HOURS = 24

logger = logging.getLogger("scheduler")

TASHKENT = pytz.timezone("Asia/Tashkent")


async def expire_promos() -> None:
    """valid_until o'tgan faol promokodlarni nofaol qiladi."""
    now = datetime.now(timezone.utc)
    async with SessionLocal() as session:
        result = await session.execute(
            update(PromoCode)
            .where(PromoCode.is_active.is_(True), PromoCode.valid_until.is_not(None), PromoCode.valid_until < now)
            .values(is_active=False)
        )
        await session.commit()
        if result.rowcount:
            logger.info("Muddati tugagan %s promokod o'chirildi", result.rowcount)


async def low_stock_alert() -> None:
    """Kam qolgan mahsulotlar haqida adminlarga ogohlantirish."""
    async with SessionLocal() as session:
        products = await report_service.low_stock_products(session, threshold=5)
    if not products:
        return
    lines = "\n".join(f"• {p.name}: {p.stock_qty} dona" for p in products)
    await notify_service.notify_admins(f"⚠️ <b>Kam qoldi</b> (5 donadan kam):\n\n{lines}")


async def daily_report() -> None:
    """Kunlik savdo va foyda hisobotini adminlarga yuboradi."""
    async with SessionLocal() as session:
        data = await report_service.daily_sales(session)
        tops = await report_service.top_products(session, limit=5, days=1)
    top_lines = "\n".join(f"  {i + 1}. {t['name']} — {t['qty_sold']} dona" for i, t in enumerate(tops))
    await notify_service.notify_admins(
        f"📊 <b>Kunlik hisobot ({data['date']})</b>\n\n"
        f"Buyurtmalar: {data['orders_count']} ta\n"
        f"Daromad: {format_money(data['revenue'])}\n"
        f"Foyda: {format_money(data['profit'])}\n"
        + (f"\n🔥 Top mahsulotlar:\n{top_lines}" if top_lines else "")
    )


async def cancel_stale_orders() -> None:
    """To'lanmagan eski buyurtmalarni bekor qiladi (qoldiq omborga qaytadi)."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=STALE_ORDER_HOURS)
    async with SessionLocal() as session:
        stale = (
            await session.execute(
                select(Order.id).where(
                    Order.status == OrderStatus.NEW.value,
                    Order.payment_status == PaymentStatus.UNPAID.value,
                    Order.created_at < cutoff,
                )
            )
        ).scalars().all()
        for order_id in stale:
            try:
                await order_service.set_status(session, order_id, OrderStatus.CANCELLED.value)
            except Exception:  # bir buyurtma xatosi qolganlarini to'xtatmasin
                logger.warning("Buyurtma #%s bekor qilinmadi", order_id)
    if stale:
        logger.info("%s ta to'lanmagan eski buyurtma bekor qilindi", len(stale))


def create_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=TASHKENT)
    scheduler.add_job(expire_promos, CronTrigger(minute=5), id="expire_promos", replace_existing=True)
    scheduler.add_job(cancel_stale_orders, CronTrigger(minute=15), id="cancel_stale_orders", replace_existing=True)
    scheduler.add_job(low_stock_alert, CronTrigger(hour=9, minute=0), id="low_stock_alert", replace_existing=True)
    scheduler.add_job(daily_report, CronTrigger(hour=21, minute=0), id="daily_report", replace_existing=True)
    return scheduler
