"""Async SQLAlchemy engine, session va deklarativ Base.

Pool kichik tutilgan (pool_size=5, max_overflow=5) — postgres max_connections=30
ga mos, minimal RAM. SQLite (dev) da pool sozlamalari qo'llanmaydi.
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """Barcha modellar shu Base'dan meros oladi."""


# SQLite uchun pool argumentlari boshqacha — shuning uchun ajratamiz.
_engine_kwargs: dict = {
    "echo": settings.debug,
    "pool_pre_ping": True,  # uzilib qolgan ulanishni avtomatik tiklaydi
}
if not settings.is_sqlite:
    _engine_kwargs.update(
        pool_size=5,        # doimiy ochiq ulanishlar (minimal)
        max_overflow=5,     # qo'shimcha tig'iz paytda (jami ≤10)
        pool_recycle=1800,  # 30 daqiqada ulanishni yangilaydi
    )

engine = create_async_engine(settings.sqlalchemy_url, **_engine_kwargs)

# expire_on_commit=False — commit'dan keyin obyektlar ishlatilaversin
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — har so'rovga bitta session, oxirida yopiladi."""
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
