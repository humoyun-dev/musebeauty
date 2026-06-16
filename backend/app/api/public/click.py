"""Click webhook skeleti — Prepare (action=0) va Complete (action=1).

Click form-urlencoded yuboradi va MD5 imzo bilan keladi. Bu skelet imzoni
tekshiradi, buyurtmani topadi va Complete'da to'lovni yozib buyurtmani 'tolandi'
qiladi. Ishga tushirishdan oldin Click kabinetidan service_id/secret_key kerak.

Idempotentlik: order.payment_status orqali (alohida tranzaksiya jadvali keyin
qo'shilishi mumkin). Hujjat: https://docs.click.uz/
"""
import hashlib
from decimal import Decimal

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models import Order, OrderStatus, Payment, PaymentMethod, PaymentStatus
from app.services import order as order_service

router = APIRouter(prefix="/click", tags=["click"])

# Click xato kodlari
OK = 0
ERR_SIGN = -1
ERR_AMOUNT = -2
ERR_ACTION = -3
ERR_ALREADY_PAID = -4
ERR_ORDER_NOT_FOUND = -5
ERR_DISABLED = -9


def _md5(*parts) -> str:
    return hashlib.md5("".join(str(p) for p in parts).encode()).hexdigest()


def _resp(data: dict, error: int, note: str) -> dict:
    return {**data, "error": error, "error_note": note}


@router.post("/prepare")
async def prepare(request: Request, db: AsyncSession = Depends(get_db)):
    form = dict((await request.form()))
    base = {
        "click_trans_id": form.get("click_trans_id"),
        "merchant_trans_id": form.get("merchant_trans_id"),
    }
    if not settings.click_enabled:
        return _resp(base, ERR_DISABLED, "Click o'chirilgan")

    expected_sign = _md5(
        form.get("click_trans_id", ""),
        form.get("service_id", ""),
        settings.click_secret_key,
        form.get("merchant_trans_id", ""),
        form.get("amount", ""),
        form.get("action", ""),
        form.get("sign_time", ""),
    )
    if expected_sign != form.get("sign_string"):
        return _resp(base, ERR_SIGN, "Imzo noto'g'ri")

    order = await db.get(Order, int(form.get("merchant_trans_id") or 0))
    if order is None or order.status == OrderStatus.CANCELLED.value:
        return _resp(base, ERR_ORDER_NOT_FOUND, "Buyurtma topilmadi")
    if Decimal(form.get("amount", "0")) != Decimal(order.total):
        return _resp(base, ERR_AMOUNT, "Summa noto'g'ri")
    if order.payment_status == PaymentStatus.PAID.value:
        return _resp(base, ERR_ALREADY_PAID, "Allaqachon to'langan")

    base["merchant_prepare_id"] = str(order.id)
    return _resp(base, OK, "Success")


@router.post("/complete")
async def complete(request: Request, db: AsyncSession = Depends(get_db)):
    form = dict((await request.form()))
    base = {
        "click_trans_id": form.get("click_trans_id"),
        "merchant_trans_id": form.get("merchant_trans_id"),
    }
    if not settings.click_enabled:
        return _resp(base, ERR_DISABLED, "Click o'chirilgan")

    expected_sign = _md5(
        form.get("click_trans_id", ""),
        form.get("service_id", ""),
        settings.click_secret_key,
        form.get("merchant_trans_id", ""),
        form.get("merchant_prepare_id", ""),
        form.get("amount", ""),
        form.get("action", ""),
        form.get("sign_time", ""),
    )
    if expected_sign != form.get("sign_string"):
        return _resp(base, ERR_SIGN, "Imzo noto'g'ri")

    order = await db.get(Order, int(form.get("merchant_trans_id") or 0))
    if order is None:
        return _resp(base, ERR_ORDER_NOT_FOUND, "Buyurtma topilmadi")

    # Click bekor qildi (error < 0)
    if int(form.get("error", 0)) < 0:
        return _resp(base, ERR_ACTION, "Tranzaksiya bekor qilindi")

    base["merchant_confirm_id"] = str(order.id)

    if order.payment_status == PaymentStatus.PAID.value:
        return _resp(base, OK, "Success")  # idempotent

    db.add(
        Payment(
            order_id=order.id,
            amount=order.total,
            method=PaymentMethod.CLICK.value,
            is_confirmed=True,
        )
    )
    await db.commit()
    if order.status == OrderStatus.NEW.value:
        await order_service.set_status(db, order.id, OrderStatus.PAID.value)

    return _resp(base, OK, "Success")
