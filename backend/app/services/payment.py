"""To'lov servisi — qo'lda to'lov cheki qabul qilish va tasdiqlash.

Mijoz chek/screenshot yuboradi → Payment(is_confirmed=False) yoziladi.
Admin panelда (3-bosqich) tasdiqlanganda buyurtma "to'landi"ga o'tadi.
"""
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import OrderStatus, Payment, PaymentMethod
from app.services import order as order_service


async def list_payments(
    session: AsyncSession, *, only_pending: bool = False, limit: int = 100
) -> list[Payment]:
    """Admin: to'lovlar ro'yxati (faqat tasdiqlanmaganlar yoki barchasi)."""
    stmt = select(Payment).order_by(Payment.created_at.desc()).limit(limit)
    if only_pending:
        stmt = stmt.where(Payment.is_confirmed.is_(False))
    return list((await session.execute(stmt)).scalars().all())


async def submit_receipt(
    session: AsyncSession,
    *,
    order_id: int,
    amount: Decimal,
    screenshot_url: str,
    method: str = PaymentMethod.MANUAL_CARD.value,
) -> Payment:
    """Mijoz yuborgan chekni saqlaydi (tasdiqlanmagan holatda)."""
    payment = Payment(
        order_id=order_id,
        amount=amount,
        method=method,
        screenshot_url=screenshot_url,
        is_confirmed=False,
    )
    session.add(payment)
    await session.commit()
    await session.refresh(payment)
    return payment


async def confirm_payment(
    session: AsyncSession, *, payment_id: int, admin_id: int | None = None
) -> Payment:
    """Admin to'lovni tasdiqlaydi → buyurtma 'to'landi'ga o'tadi."""
    payment = await session.get(Payment, payment_id)
    if payment is None:
        raise ValueError(f"To'lov topilmadi (id={payment_id})")

    payment.is_confirmed = True
    payment.confirmed_by = admin_id
    payment.confirmed_at = datetime.now(timezone.utc)
    await session.commit()

    # Buyurtmani 'to'landi'ga o'tkazamiz (holat zanjiri tekshiradi)
    await order_service.set_status(session, payment.order_id, OrderStatus.PAID.value)
    await session.refresh(payment)
    return payment
