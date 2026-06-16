"""Marketing modellari: discounts, promo_codes, promo_redemptions."""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import (
    DiscountType,
    Money,
    MoneyT,
    PromoType,
    Scope,
    TimestampMixin,
)


class Discount(Base):
    """Kodsiz chegirma/aksiya (avtomatik qo'llanadi)."""

    __tablename__ = "discounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(
        String(20), default=DiscountType.PERCENT.value, nullable=False
    )
    value: Mapped[MoneyT] = mapped_column(Money, nullable=False)  # % yoki summa
    scope: Mapped[str] = mapped_column(String(20), default=Scope.ALL.value, nullable=False)
    target_id: Mapped[int | None] = mapped_column(Integer)  # category_id yoki product_id

    valid_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class PromoCode(Base):
    """Kod bilan chegirma (mijoz checkout'da kiritadi)."""

    __tablename__ = "promo_codes"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(60), unique=True, index=True, nullable=False)
    type: Mapped[str] = mapped_column(
        String(20), default=PromoType.PERCENT.value, nullable=False
    )
    value: Mapped[MoneyT] = mapped_column(Money, default=0, nullable=False)

    min_order_amount: Mapped[MoneyT] = mapped_column(Money, default=0, nullable=False)
    max_discount: Mapped[MoneyT | None] = mapped_column(Money)  # % uchun yuqori chegara

    usage_limit: Mapped[int | None] = mapped_column(Integer)    # umumiy limit
    used_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    per_user_limit: Mapped[int | None] = mapped_column(Integer)  # bir mijozga necha marta
    first_order_only: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    scope: Mapped[str] = mapped_column(String(20), default=Scope.ALL.value, nullable=False)
    target_id: Mapped[int | None] = mapped_column(Integer)

    valid_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    redemptions: Mapped[list["PromoRedemption"]] = relationship(
        back_populates="promo_code"
    )


class PromoRedemption(Base):
    """Kim, qachon, qaysi buyurtmada promokodni ishlatdi."""

    __tablename__ = "promo_redemptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    promo_code_id: Mapped[int] = mapped_column(
        ForeignKey("promo_codes.id", ondelete="CASCADE"), index=True
    )
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"), index=True
    )
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), index=True
    )
    discount_amount: Mapped[MoneyT] = mapped_column(Money, default=0, nullable=False)
    used_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    promo_code: Mapped["PromoCode"] = relationship(back_populates="redemptions")
