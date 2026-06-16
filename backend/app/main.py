"""FastAPI ilovasi — api/public + api/admin uchun kirish nuqtasi.

1-bosqich: faqat /health (baza tekshiruvi bilan) va ildiz endpoint.
Keyingi bosqichlarda api/public va api/admin routerlari shu yerga ulanadi.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.api.admin import auth as admin_auth
from app.api.admin import customers as admin_customers
from app.api.admin import inventory as admin_inventory
from app.api.admin import marketing as admin_marketing
from app.api.admin import orders as admin_orders
from app.api.admin import payments as admin_payments
from app.api.admin import products as admin_products
from app.api.admin import reports as admin_reports
from app.api.admin import upload as admin_upload
from app.api.public import catalog as public_catalog
from app.api.public import cart as public_cart
from app.api.public import click as public_click
from app.api.public import order as public_order
from app.api.public import payme as public_payme
from app.api.public import promotions as public_promotions
from app.core.config import settings
from app.core.database import engine
from app.tasks.scheduler import create_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ishga tushganda: rejalashtirilgan ishlarni boshlaymiz (faqat api jarayonida,
    # 1 worker — bitta nusxa, takrorlanmaydi).
    scheduler = create_scheduler()
    scheduler.start()
    yield
    # To'xtaganda: scheduler va ulanishlarni toza yopamiz.
    scheduler.shutdown(wait=False)
    await engine.dispose()


app = FastAPI(
    title="MUSE BEAUTY API",
    version="0.1.0",
    debug=settings.debug,
    lifespan=lifespan,
)

# CORS — admin panel (alohida subdomain) va mahalliy Vite dev serveri uchun.
# Production'da nginx bir xil origin'dan proxy qiladi, lekin dev'da kerak.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"https://{settings.admin_domain}",
        f"https://{settings.public_domain}",
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict:
    return {"app": "muse-beauty", "status": "ok"}


@app.get("/health")
async def health() -> dict:
    """Liveness + baza ulanishini tekshiradi (docker healthcheck/monitoring uchun)."""
    db_ok = True
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        db_ok = False
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "up" if db_ok else "down",
        "environment": settings.environment,
    }


# ─── api/public routerlari (bot + website) ───
app.include_router(public_catalog.router, prefix="/api/public")
app.include_router(public_cart.router, prefix="/api/public")
app.include_router(public_order.router, prefix="/api/public")
app.include_router(public_promotions.router, prefix="/api/public")
# To'lov provayderlari webhook'lari (auth ichida — Basic/imzo)
app.include_router(public_payme.router, prefix="/api/public")
app.include_router(public_click.router, prefix="/api/public")

# ─── api/admin routerlari (JWT auth majburiy) ───
app.include_router(admin_auth.router, prefix="/api/admin")
app.include_router(admin_products.router, prefix="/api/admin")
app.include_router(admin_orders.router, prefix="/api/admin")
app.include_router(admin_inventory.router, prefix="/api/admin")
app.include_router(admin_payments.router, prefix="/api/admin")
app.include_router(admin_customers.router, prefix="/api/admin")
app.include_router(admin_marketing.router, prefix="/api/admin")
app.include_router(admin_reports.router, prefix="/api/admin")
app.include_router(admin_upload.router, prefix="/api/admin")

# Yuklangan rasmlar (disk). Prod'da nginx /media ni to'g'ridan beradi (tezroq);
# bu mount dev va zaxira uchun. check_dir=False — papka hali yo'q bo'lsa ham xato bermaydi.
app.mount("/media", StaticFiles(directory=settings.media_root, check_dir=False), name="media")
