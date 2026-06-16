"""Admin foydalanuvchi servisi — autentifikatsiya va yaratish."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models import Admin, AdminRole


async def authenticate(session: AsyncSession, username: str, password: str) -> Admin | None:
    """Login: username + parol to'g'ri va admin faol bo'lsa — Admin, aks holda None."""
    admin = (
        await session.execute(select(Admin).where(Admin.username == username))
    ).scalar_one_or_none()
    if admin is None or not admin.is_active:
        return None
    if not verify_password(password, admin.password_hash):
        return None
    return admin


async def get_admin(session: AsyncSession, admin_id: int) -> Admin | None:
    return await session.get(Admin, admin_id)


async def create_admin(
    session: AsyncSession,
    *,
    username: str,
    password: str,
    role: str = AdminRole.MANAGER.value,
) -> Admin:
    """Yangi admin yaratadi (mavjud bo'lsa parol/rolни yangilaydi)."""
    existing = (
        await session.execute(select(Admin).where(Admin.username == username))
    ).scalar_one_or_none()
    if existing:
        existing.password_hash = hash_password(password)
        existing.role = role
        existing.is_active = True
        await session.commit()
        await session.refresh(existing)
        return existing

    admin = Admin(
        username=username,
        password_hash=hash_password(password),
        role=role,
        is_active=True,
    )
    session.add(admin)
    await session.commit()
    await session.refresh(admin)
    return admin
