"""To'lov provayderlari tranzaksiyalari (Payme/Click) — holatni kuzatish uchun.

Payme merchant protokoli tranzaksiya holatini (yaratildi/bajarildi/bekor) va
ms timestamp'larni talab qiladi — shuning uchun alohida jadval.
"""
from sqlalchemy import BigInteger, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import Money, MoneyT, TimestampMixin


class PaymeTransaction(Base, TimestampMixin):
    __tablename__ = "payme_transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Payme tomonidagi tranzaksiya id (paycom)
    paycom_id: Mapped[str] = mapped_column(String(60), unique=True, index=True, nullable=False)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), index=True
    )
    amount: Mapped[MoneyT] = mapped_column(Money, nullable=False)  # so'mда

    # Payme holatlari: 1=yaratildi, 2=bajarildi, -1=bekor(create), -2=bekor(perform)
    state: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    reason: Mapped[int | None] = mapped_column(Integer)  # bekor sababi (Payme kodi)

    # ms timestamp (Payme shu formatda ishlaydi)
    create_time: Mapped[int] = mapped_column(BigInteger, default=0)
    perform_time: Mapped[int] = mapped_column(BigInteger, default=0)
    cancel_time: Mapped[int] = mapped_column(BigInteger, default=0)
