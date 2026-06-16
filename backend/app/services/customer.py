"""Mijoz servisi — Telegram va website mijozlarini topish/yaratish."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Customer


async def get_by_telegram(session: AsyncSession, telegram_id: int) -> Customer | None:
    return (
        await session.execute(select(Customer).where(Customer.telegram_id == telegram_id))
    ).scalar_one_or_none()


async def get_or_create_web_customer(
    session: AsyncSession, *, name: str | None, phone: str
) -> Customer:
    """Website buyurtmasi uchun mijoz. Telefon bo'yicha bor bo'lsa (Telegram'da
    ro'yxatdan o'tgan ham) — o'shani qaytaradi; aks holda yangi (telegram_id=NULL)."""
    phone = phone.strip()
    existing = (
        await session.execute(
            select(Customer).where(Customer.phone == phone).order_by(Customer.id)
        )
    ).scalars().first()
    if existing is not None:
        if name and not existing.name:
            existing.name = name
        return existing

    customer = Customer(telegram_id=None, name=name, phone=phone)
    session.add(customer)
    await session.flush()
    return customer
