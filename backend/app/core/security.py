"""Admin autentifikatsiyasi: parol hash (bcrypt) va JWT token.

Bot tomonda auth yo'q (Telegram ID orqali) — bu fayl faqat admin panel uchun.
"""
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# bcrypt — sekin va tuzli hash (parollar uchun standart)
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ─────────────────────────── Parol ───────────────────────────
def hash_password(plain: str) -> str:
    """Ochiq parolni bcrypt hash'ga aylantiradi (bazaga shu saqlanadi)."""
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Kiritilgan parolni saqlangan hash bilan solishtiradi."""
    return _pwd_context.verify(plain, hashed)


# ─────────────────────────── JWT ───────────────────────────
def create_access_token(subject: str | int, extra: dict | None = None) -> str:
    """Admin uchun imzolangan JWT yaratadi.

    subject — odatda admin id; extra — qo'shimcha da'volar (masalan role).
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload: dict = {"sub": str(subject), "exp": expire}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict | None:
    """Tokenni tekshiradi va da'volarni qaytaradi; yaroqsiz bo'lsa None."""
    try:
        return jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
    except JWTError:
        return None
