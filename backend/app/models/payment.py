"""To'lov modeli: payments.

Qo'lda to'lov: mijoz chek/screenshot yuboradi → is_confirmed=false bilan saqlanadi.
Admin panelda tasdiqlangach is_confirmed=true bo'ladi va buyurtma "to'landi"ga o'tadi.
"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import (
    Money,
    MoneyT,
    PaymentMethod,
    TimestampMixin,
)


class Payment(Base, TimestampMixin):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), index=True
    )
    amount: Mapped[MoneyT] = mapped_column(Money, nullable=False)
    method: Mapped[str] = mapped_column(
        String(20), default=PaymentMethod.MANUAL_CARD.value, nullable=False
    )
    screenshot_url: Mapped[str | None] = mapped_column(String(500))  # qo'lda to'lov cheki

    is_confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    confirmed_by: Mapped[int | None] = mapped_column(
        ForeignKey("admins.id", ondelete="SET NULL")
    )
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    order: Mapped["Order"] = relationship(back_populates="payments")  # noqa: F821
