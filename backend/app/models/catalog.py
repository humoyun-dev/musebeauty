"""Katalog va ombor modellari: categories, products, supply_batches, batch_items."""
from datetime import date

from sqlalchemy import JSON, Boolean, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import Money, MoneyT, TimestampMixin


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(140), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    products: Mapped[list["Product"]] = relationship(back_populates="category")


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(500))         # muqova (ro'yxat thumbnaillari)
    # Barcha rasmlar (tartibli, [0] = muqova). image_url shu ro'yxat bilan sinxron.
    gallery: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    price: Mapped[MoneyT] = mapped_column(Money, nullable=False)        # joriy sotuv narxi
    cost_price: Mapped[MoneyT] = mapped_column(Money, default=0)        # tannarx (foyda hisobi)
    stock_qty: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # ombor qoldig'i

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    category: Mapped["Category | None"] = relationship(back_populates="products")

    @property
    def images(self) -> list[str]:
        """Albom uchun barcha rasmlar (tartibli). Eski mahsulotlarda gallery
        bo'sh bo'lsa — image_url ga tushadi."""
        if self.gallery:
            return list(self.gallery)
        return [self.image_url] if self.image_url else []


class SupplyBatch(Base):
    """Koreadan kelgan ta'minot partiyasi."""

    __tablename__ = "supply_batches"

    id: Mapped[int] = mapped_column(primary_key=True)
    supplier: Mapped[str | None] = mapped_column(String(200))
    arrival_date: Mapped[date | None] = mapped_column(Date)
    total_cost: Mapped[MoneyT] = mapped_column(Money, default=0)
    note: Mapped[str | None] = mapped_column(Text)

    items: Mapped[list["BatchItem"]] = relationship(
        back_populates="batch", cascade="all, delete-orphan"
    )


class BatchItem(Base):
    """Partiya ichidagi bitta mahsulot qatori."""

    __tablename__ = "batch_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[int] = mapped_column(
        ForeignKey("supply_batches.id", ondelete="CASCADE"), index=True
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"), index=True
    )
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_cost: Mapped[MoneyT] = mapped_column(Money, nullable=False)  # dona tannarxi

    batch: Mapped["SupplyBatch"] = relationship(back_populates="items")
