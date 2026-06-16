"""Admin endpointlari uchun umumiy bog'liqliklar (JWT himoyasi)."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models import Admin, AdminRole
from app.services import admin as admin_service

# Authorization: Bearer <token>
_bearer = HTTPBearer(auto_error=False)

_UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Avtorizatsiya talab qilinadi",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_admin(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> Admin:
    """Tokenni tekshiradi va faol adminni qaytaradi; aks holда 401."""
    if creds is None:
        raise _UNAUTHORIZED
    payload = decode_access_token(creds.credentials)
    if payload is None or "sub" not in payload:
        raise _UNAUTHORIZED
    try:
        admin_id = int(payload["sub"])
    except (TypeError, ValueError):
        raise _UNAUTHORIZED
    admin = await admin_service.get_admin(db, admin_id)
    if admin is None or not admin.is_active:
        raise _UNAUTHORIZED
    return admin


def require_role(*roles: str):
    """Ma'lum rol(lar)ni talab qiluvchi dependency. superadmin har doim o'tadi."""

    async def checker(admin: Admin = Depends(get_current_admin)) -> Admin:
        if admin.role == AdminRole.SUPERADMIN.value or admin.role in roles:
            return admin
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Ruxsat yo'q"
        )

    return checker
