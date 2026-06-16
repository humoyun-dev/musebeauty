"""Admin: hisobotlar — dashboard, kunlik savdo, top mahsulotlar."""
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.admin.deps import get_current_admin
from app.core.database import get_db
from app.services import report as report_service

router = APIRouter(prefix="/reports", tags=["admin-reports"], dependencies=[Depends(get_current_admin)])


@router.get("/dashboard")
async def dashboard(db: AsyncSession = Depends(get_db)):
    return await report_service.dashboard(db)


@router.get("/daily")
async def daily(day: date | None = None, db: AsyncSession = Depends(get_db)):
    return await report_service.daily_sales(db, day)


@router.get("/top-products")
async def top_products(limit: int = 10, days: int | None = None, db: AsyncSession = Depends(get_db)):
    return await report_service.top_products(db, limit=limit, days=days)
