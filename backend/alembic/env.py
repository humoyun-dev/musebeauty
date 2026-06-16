"""Alembic muhiti — async SQLAlchemy bilan.

Ulanish satri va metadata app kodidan olinadi (yagona manba):
  • settings.sqlalchemy_url  — qaysi bazaga
  • Base.metadata            — qaysi jadvallar (autogenerate uchun)
"""
import asyncio
from logging.config import fileConfig

from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Barcha modellarni import qilamiz — Base.metadata to'lishi uchun SHART.
from app.core.config import settings
from app.models import Base  # noqa: F401  (app.models barcha modelni yuklaydi)

config = context.config

# alembic.ini dagi sqlalchemy.url ni kod bilan to'ldiramiz (.env dan)
config.set_main_option("sqlalchemy.url", settings.sqlalchemy_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """URL bilan (jonli ulanishsiz) — SQL chiqaradi."""
    context.configure(
        url=settings.sqlalchemy_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,        # ustun tipi o'zgarishini ham sezadi
        render_as_batch=settings.is_sqlite,  # SQLite ALTER cheklovi uchun
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Async engine yaratib, sinxron migratsiyani ulanish ustida bajaradi."""
    connectable = async_engine_from_config(
        {"sqlalchemy.url": settings.sqlalchemy_url},
        prefix="sqlalchemy.",
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
