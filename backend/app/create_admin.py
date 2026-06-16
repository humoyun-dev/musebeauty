"""Admin yaratish CLI — `python -m app.create_admin <username> <password> [role]`.

Mavjud bo'lsa parol/rolни yangilaydi (idempotent). role: superadmin|manager|operator.
Misol:
  docker compose exec api python -m app.create_admin admin "KuchliParol123" superadmin
"""
import asyncio
import sys

from app.core.database import SessionLocal
from app.models import AdminRole
from app.services import admin as admin_service


async def main() -> None:
    if len(sys.argv) < 3:
        print("Foydalanish: python -m app.create_admin <username> <password> [role]")
        raise SystemExit(1)

    username = sys.argv[1]
    password = sys.argv[2]
    role = sys.argv[3] if len(sys.argv) > 3 else AdminRole.MANAGER.value

    valid_roles = {r.value for r in AdminRole}
    if role not in valid_roles:
        print(f"Noto'g'ri rol '{role}'. Ruxsat: {', '.join(valid_roles)}")
        raise SystemExit(1)

    async with SessionLocal() as session:
        admin = await admin_service.create_admin(
            session, username=username, password=password, role=role
        )
    print(f"✅ Admin tayyor: id={admin.id} username='{admin.username}' role='{admin.role}'")


if __name__ == "__main__":
    asyncio.run(main())
