"""Payme merchant (Paycom) JSON-RPC protokoli — avtomatik to'lov.

Payme summani TIYINда yuboradi (1 so'm = 100 tiyin), vaqtni ms timestamp'da.
`account.order_id` orqali buyurtmani topamiz. Perform bo'lganda buyurtma
avtomatik 'tolandi' bo'ladi (qo'lda tasdiq shart emas).

Hujjat: https://developer.help.paycom.uz/protokol-merchant-api/
"""
import base64
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

from app.models import (
    Order,
    OrderStatus,
    Payment,
    PaymentMethod,
    PaymentStatus,
    PaymeTransaction,
)

# Payme tranzaksiya holatlari
STATE_CREATED = 1
STATE_COMPLETED = 2
STATE_CANCELLED = -1
STATE_CANCELLED_AFTER_COMPLETE = -2

# Xato kodlari (Payme)
ERR_AUTH = -32504
ERR_METHOD_NOT_FOUND = -32601
ERR_ORDER_NOT_FOUND = -31050
ERR_INVALID_AMOUNT = -31001
ERR_CANT_PERFORM = -31008
ERR_TX_NOT_FOUND = -31003
ERR_ORDER_IN_PROCESS = -31099


def _msg(text: str) -> dict:
    """Payme uch tilli xabar kutadi."""
    return {"ru": text, "uz": text, "en": text}


def now_ms() -> int:
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def checkout_url(order_id: int, amount_tiyin: int) -> str:
    """Payme checkout tugmasi URL'i (website uchun).
    Format: base64('m=MERCHANT;ac.order_id=ID;a=TIYIN') → checkout.paycom.uz/<...>."""
    params = f"m={settings.payme_merchant_id};ac.order_id={order_id};a={amount_tiyin}"
    return f"https://checkout.paycom.uz/{base64.b64encode(params.encode()).decode()}"


class PaymeError(Exception):
    def __init__(self, code: int, message, data: str | None = None):
        self.code = code
        self.message = message if isinstance(message, dict) else _msg(str(message))
        self.data = data
        super().__init__(str(message))


class PaymeService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_order_checked(self, params: dict) -> Order:
        account = params.get("account") or {}
        raw = account.get("order_id")
        try:
            order_id = int(raw)
        except (TypeError, ValueError):
            raise PaymeError(ERR_ORDER_NOT_FOUND, "Buyurtma topilmadi", data="order_id")

        order = await self.session.get(Order, order_id)
        if order is None or order.status == OrderStatus.CANCELLED.value:
            raise PaymeError(ERR_ORDER_NOT_FOUND, "Buyurtma topilmadi", data="order_id")

        expected = int(Decimal(order.total) * 100)  # so'm → tiyin
        if int(params.get("amount", 0)) != expected:
            raise PaymeError(ERR_INVALID_AMOUNT, "Summa noto'g'ri", data="amount")
        return order

    async def _get_tx(self, paycom_id: str) -> PaymeTransaction | None:
        return (
            await self.session.execute(
                select(PaymeTransaction).where(PaymeTransaction.paycom_id == paycom_id)
            )
        ).scalar_one_or_none()

    # ─────────────── Metodlar ───────────────
    async def check_perform_transaction(self, params: dict) -> dict:
        order = await self._get_order_checked(params)
        if order.payment_status == PaymentStatus.PAID.value:
            raise PaymeError(ERR_CANT_PERFORM, "Buyurtma allaqachon to'langan")
        return {"allow": True}

    async def create_transaction(self, params: dict) -> dict:
        paycom_id = params["id"]
        existing = await self._get_tx(paycom_id)
        if existing is not None:
            if existing.state == STATE_CREATED:
                return {
                    "create_time": existing.create_time,
                    "transaction": str(existing.id),
                    "state": STATE_CREATED,
                }
            raise PaymeError(ERR_CANT_PERFORM, "Tranzaksiya holati noto'g'ri")

        order = await self._get_order_checked(params)

        # Shu buyurtmada boshqa faol tranzaksiya bo'lmasligi kerak
        active = (
            await self.session.execute(
                select(PaymeTransaction).where(
                    PaymeTransaction.order_id == order.id,
                    PaymeTransaction.state == STATE_CREATED,
                )
            )
        ).scalar_one_or_none()
        if active is not None:
            raise PaymeError(ERR_ORDER_IN_PROCESS, "Buyurtmada faol tranzaksiya bor", data="order_id")

        tx = PaymeTransaction(
            paycom_id=paycom_id,
            order_id=order.id,
            amount=order.total,
            state=STATE_CREATED,
            create_time=int(params.get("time", now_ms())),
        )
        self.session.add(tx)
        await self.session.commit()
        await self.session.refresh(tx)
        return {"create_time": tx.create_time, "transaction": str(tx.id), "state": STATE_CREATED}

    async def perform_transaction(self, params: dict) -> dict:
        tx = await self._get_tx(params["id"])
        if tx is None:
            raise PaymeError(ERR_TX_NOT_FOUND, "Tranzaksiya topilmadi")

        if tx.state == STATE_COMPLETED:
            return {"transaction": str(tx.id), "perform_time": tx.perform_time, "state": STATE_COMPLETED}
        if tx.state != STATE_CREATED:
            raise PaymeError(ERR_CANT_PERFORM, "Tranzaksiya holati noto'g'ri")

        from app.services import order as order_service

        tx.perform_time = now_ms()
        tx.state = STATE_COMPLETED

        # To'lovni yozamiz va buyurtmani 'tolandi' qilamiz
        self.session.add(
            Payment(
                order_id=tx.order_id,
                amount=tx.amount,
                method=PaymentMethod.PAYME.value,
                is_confirmed=True,
                confirmed_at=datetime.now(timezone.utc),
            )
        )
        await self.session.commit()

        order = await self.session.get(Order, tx.order_id)
        if order is not None and order.status == OrderStatus.NEW.value:
            await order_service.set_status(self.session, order.id, OrderStatus.PAID.value)

        return {"transaction": str(tx.id), "perform_time": tx.perform_time, "state": STATE_COMPLETED}

    async def cancel_transaction(self, params: dict) -> dict:
        tx = await self._get_tx(params["id"])
        if tx is None:
            raise PaymeError(ERR_TX_NOT_FOUND, "Tranzaksiya topilmadi")

        reason = params.get("reason")
        if tx.state == STATE_CREATED:
            tx.state = STATE_CANCELLED
            tx.cancel_time = now_ms()
            tx.reason = reason
            await self.session.commit()
        elif tx.state == STATE_COMPLETED:
            from app.services import order as order_service
            from app.services.order import InvalidStatusTransition

            tx.state = STATE_CANCELLED_AFTER_COMPLETE
            tx.cancel_time = now_ms()
            tx.reason = reason
            await self.session.commit()
            # Pul qaytarildi: buyurtmani bekor qilib qoldiqni qaytaramiz
            try:
                await order_service.set_status(self.session, tx.order_id, OrderStatus.CANCELLED.value)
            except InvalidStatusTransition:
                pass
            order = await self.session.get(Order, tx.order_id)
            if order is not None:
                order.payment_status = PaymentStatus.REFUNDED.value
                await self.session.commit()

        return {"transaction": str(tx.id), "cancel_time": tx.cancel_time, "state": tx.state}

    async def check_transaction(self, params: dict) -> dict:
        tx = await self._get_tx(params["id"])
        if tx is None:
            raise PaymeError(ERR_TX_NOT_FOUND, "Tranzaksiya topilmadi")
        return {
            "create_time": tx.create_time,
            "perform_time": tx.perform_time,
            "cancel_time": tx.cancel_time,
            "transaction": str(tx.id),
            "state": tx.state,
            "reason": tx.reason,
        }

    async def get_statement(self, params: dict) -> dict:
        frm = int(params.get("from", 0))
        to = int(params.get("to", now_ms()))
        rows = (
            await self.session.execute(
                select(PaymeTransaction).where(
                    PaymeTransaction.create_time >= frm,
                    PaymeTransaction.create_time <= to,
                )
            )
        ).scalars().all()
        return {
            "transactions": [
                {
                    "id": t.paycom_id,
                    "time": t.create_time,
                    "amount": int(Decimal(t.amount) * 100),
                    "account": {"order_id": str(t.order_id)},
                    "create_time": t.create_time,
                    "perform_time": t.perform_time,
                    "cancel_time": t.cancel_time,
                    "transaction": str(t.id),
                    "state": t.state,
                    "reason": t.reason,
                }
                for t in rows
            ]
        }


_METHODS = {
    "CheckPerformTransaction": "check_perform_transaction",
    "CreateTransaction": "create_transaction",
    "PerformTransaction": "perform_transaction",
    "CancelTransaction": "cancel_transaction",
    "CheckTransaction": "check_transaction",
    "GetStatement": "get_statement",
}


async def handle(session: AsyncSession, method: str, params: dict) -> dict:
    """Metodni bajaradi yoki PaymeError tashlaydi."""
    attr = _METHODS.get(method)
    if attr is None:
        raise PaymeError(ERR_METHOD_NOT_FOUND, "Metod topilmadi")
    service = PaymeService(session)
    return await getattr(service, attr)(params)
