"""Admin: mijozlar ro'yxati (CRM-lite)."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.admin.deps import get_current_admin
from app.core.database import get_db
from app.models import Customer
from app.schemas.admin import CustomerOut

router = APIRouter(prefix="/customers", tags=["admin-customers"], dependencies=[Depends(get_current_admin)])


@router.get("", response_model=list[CustomerOut])
async def customers(limit: int = 200, offset: int = 0, db: AsyncSession = Depends(get_db)):
    stmt = select(Customer).order_by(Customer.created_at.desc()).limit(limit).offset(offset)
    return list((await db.execute(stmt)).scalars().all())
