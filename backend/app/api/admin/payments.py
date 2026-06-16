"""Admin: to'lovlar — ro'yxat va tasdiqlash (chek ko'rib, tasdiqlash)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.admin.deps import get_current_admin
from app.core.database import get_db
from app.models import Admin
from app.schemas.admin import PaymentOut
from app.services import payment as payment_service

router = APIRouter(prefix="/payments", tags=["admin-payments"])


@router.get("", response_model=list[PaymentOut], dependencies=[Depends(get_current_admin)])
async def payments(
    pending: bool = False, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    return await payment_service.list_payments(db, only_pending=pending, limit=limit)


@router.post("/{payment_id}/confirm", response_model=PaymentOut)
async def confirm(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    try:
        return await payment_service.confirm_payment(
            db, payment_id=payment_id, admin_id=admin.id
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
