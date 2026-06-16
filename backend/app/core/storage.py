"""Fayl saqlash — rasm yuklash uchun. DISK (volume) yoki S3-mos (Cloudflare R2).

Interfeys bitta: save_image(content, name) → ommaviy URL. Backend'ni
config.storage_backend belgilaydi. Mantiq bir joyda — almashtirish oson.
"""
import asyncio
import os
import pathlib
import uuid
from functools import lru_cache

from app.core.config import settings

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_BYTES = 5 * 1024 * 1024  # 5MB

# Kengaytma → Content-Type. R2 obyektni shu sarlavha bilan beradi, aks holda
# brauzer/Telegram rasmni "octet-stream" deb yuklab oladi (ko'rsatmaydi).
CONTENT_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
}


class UploadError(Exception):
    pass


def _safe_ext(filename: str) -> str:
    ext = pathlib.Path(filename or "").suffix.lower()
    if ext not in ALLOWED_EXT:
        raise UploadError("Faqat rasm (jpg, png, webp, gif) yuklash mumkin")
    return ext


async def save_image(content: bytes, filename: str, *, subdir: str = "products") -> str:
    """Rasmni saqlaydi va ommaviy URL qaytaradi."""
    if len(content) > MAX_BYTES:
        raise UploadError("Rasm hajmi 5MB dan oshmasligi kerak")
    ext = _safe_ext(filename)
    name = f"{uuid.uuid4().hex}{ext}"

    if settings.storage_backend == "s3":
        return await _save_s3(content, f"{subdir}/{name}", ext)

    # Disk (default)
    folder = os.path.join(settings.media_root, subdir)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, name), "wb") as f:
        f.write(content)
    return f"{settings.media_url_base}/{subdir}/{name}"


@lru_cache(maxsize=1)
def _s3_client():
    """Cloudflare R2 (S3-mos) klienti. Bir marta yaratib keshlanadi.

    R2 xususiyatlari: region="auto", SigV4 imzo, path-style addressing
    (bucket hostda emas, yo'lda). Obyekt ACL'ini qo'llab-quvvatlamaydi —
    ommaviylik bucket darajasida (r2.dev yoki maxsus domen) sozlanadi.
    """
    import boto3
    from botocore.config import Config

    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
        config=Config(
            signature_version="s3v4",
            s3={"addressing_style": "path"},
        ),
    )


async def _save_s3(content: bytes, key: str, ext: str) -> str:
    """R2/S3 ga saqlash → ommaviy URL (s3_public_url/key)."""
    if not (settings.s3_endpoint and settings.s3_bucket and settings.s3_public_url):
        raise UploadError(
            "R2 sozlanmagan — S3_ENDPOINT, S3_BUCKET, S3_ACCESS_KEY, "
            "S3_SECRET_KEY, S3_PUBLIC_URL ni .env da to'ldiring"
        )
    content_type = CONTENT_TYPES.get(ext, "application/octet-stream")

    def _put() -> None:
        _s3_client().put_object(
            Bucket=settings.s3_bucket,
            Key=key,
            Body=content,
            ContentType=content_type,
            CacheControl="public, max-age=31536000, immutable",  # fayl nomi uuid — o'zgarmaydi
        )

    try:
        # boto3 sinxron — admin yuklashlari kam, threadda chaqiramiz (event loop bloklanmasin)
        await asyncio.to_thread(_put)
    except Exception as exc:  # botocore.ClientError va h.k.
        raise UploadError(f"R2 ga yuklashda xato: {exc}") from exc

    return f"{settings.s3_public_url.rstrip('/')}/{key}"
