"""Mijoz va Toshkent tumanlari modellari: customers, districts."""
from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import Money, MoneyT, TimestampMixin


class Customer(Base, TimestampMixin):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Telegram ID katta son — BigInteger. Website mijozlari uchun NULL bo'lishi
    # mumkin (ular telefon orqali aniqlanadi). UNIQUE bir nechta NULL'ga ruxsat beradi.
    telegram_id: Mapped[int | None] = mapped_column(
        BigInteger, unique=True, index=True, nullable=True
    )
    name: Mapped[str | None] = mapped_column(String(200))
    phone: Mapped[str | None] = mapped_column(String(30), index=True)

    orders: Mapped[list["Order"]] = relationship(back_populates="customer")  # noqa: F821


class District(Base):
    """Toshkent tumani + shu tumanga yetkazib berish narxi."""

    __tablename__ = "districts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    delivery_fee: Mapped[MoneyT] = mapped_column(Money, default=0, nullable=False)
