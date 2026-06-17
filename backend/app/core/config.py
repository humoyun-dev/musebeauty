"""Ilova sozlamalari — barchasi .env dan o'qiladi (kodda maxfiy qiymat yo'q).

pydantic-settings qiymatlarni .env / muhit o'zgaruvchilaridan oladi va
tiplarini tekshiradi. Bir joyda — boshqa modullar shu `settings` ni import qiladi.
"""
from functools import lru_cache

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # .env dagi ortiqcha kalitlar xato bermasin
    )

    # ─── Muhit ───
    environment: str = "production"  # production | development
    debug: bool = False

    # ─── PostgreSQL ───
    db_name: str = "musebeauty"
    db_user: str = "musebeauty"
    db_password: str = "musebeauty"
    db_host: str = "postgres"
    db_port: int = 5432
    # Agar berilsa, DB_* dan ustun turadi (masalan SQLite dev uchun):
    #   sqlite+aiosqlite:///./dev.db
    database_url: str | None = None

    # ─── Redis (FSM / savat / kesh) ───
    redis_url: str = "redis://redis:6379/0"

    # ─── Telegram bot ───
    bot_token: str = ""
    # ".env" da vergulli satr: "111,222" → ro'yxatga aylantiramiz (validator pastda)
    admin_telegram_ids: str = ""

    # ─── Xavfsizlik (admin JWT) ───
    jwt_secret: str = "CHANGE_ME"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 720

    # ─── To'lov (qo'lda) ───
    payment_card_number: str = ""
    payment_card_holder: str = ""

    # ─── Domen ───
    public_domain: str = "musebeauty.uz"
    admin_domain: str = "admin.musebeauty.uz"

    # ─── Rasm saqlash (disk yoki S3-mos: Cloudflare R2) ───
    storage_backend: str = "disk"          # disk | s3
    media_root: str = "/app/media"         # disk saqlash papkasi (volume)
    media_url_base: str = "/media"         # nginx shu yo'ldan beradi
    # R2/S3 (storage_backend=s3 bo'lsa):
    s3_endpoint: str = ""                  # R2: https://<account_id>.r2.cloudflarestorage.com
    s3_bucket: str = ""
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_region: str = "auto"                # R2 doim "auto"
    s3_public_url: str = ""                # R2: https://pub-<hash>.r2.dev yoki https://cdn.musebeauty.uz

    # ─── Payme (avtomatik to'lov) ───
    payme_enabled: bool = False
    payme_merchant_id: str = ""
    payme_key: str = ""                    # kassa kaliti (webhook Basic auth)

    # ─── Click (avtomatik to'lov) ───
    click_enabled: bool = False
    click_service_id: str = ""
    click_merchant_id: str = ""
    click_secret_key: str = ""

    # ─── Hosil qilinadigan qiymatlar ───
    @computed_field  # type: ignore[prop-decorator]
    @property
    def sqlalchemy_url(self) -> str:
        """SQLAlchemy async ulanish satri. DATABASE_URL berilsa — o'sha,
        aks holda DB_* dan PostgreSQL+asyncpg satri yig'iladi."""
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def admin_ids(self) -> list[int]:
        """ADMIN_TELEGRAM_IDS ("111,222") → [111, 222]."""
        raw = self.admin_telegram_ids.strip()
        if not raw:
            return []
        return [int(x) for x in raw.replace(" ", "").split(",") if x]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_sqlite(self) -> bool:
        return self.sqlalchemy_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    """Bir marta o'qib, keshlab beradi (har joyda bir xil nusxa)."""
    return Settings()


settings = get_settings()
