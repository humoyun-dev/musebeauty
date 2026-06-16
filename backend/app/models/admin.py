"""Admin va audit modellari: admins, audit_log."""
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import AdminRole, TimestampMixin


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(20), default=AdminRole.MANAGER.value, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class AuditLog(Base, TimestampMixin):
    """Kim nimani o'zgartirdi (ixtiyoriy, lekin foydali)."""

    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    admin_id: Mapped[int | None] = mapped_column(Integer, index=True)
    action: Mapped[str] = mapped_column(String(80), nullable=False)   # create/update/delete/confirm
    entity: Mapped[str] = mapped_column(String(80), nullable=False)   # jadval nomi
    entity_id: Mapped[int | None] = mapped_column(Integer)
