"""Admin: buyurtmalar ro'yxati, tafsilot, holat o'zgartirish."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.admin.deps import get_current_admin
from app.core.database import get_db
from app.schemas.admin import OrderAdminOut, OrderStatusUpdate
from app.services import order as order_service
from app.services.order import InvalidStatusTransition

router = APIRouter(prefix="/orders", tags=["admin-orders"], dependencies=[Depends(get_current_admin)])


@router.get("", response_model=list[OrderAdminOut])
async def orders(
    status: str | None = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    return await order_service.list_orders(db, status=status, limit=limit, offset=offset)


@router.get("/{order_id}", response_model=OrderAdminOut)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    order = await order_service.get_order(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
    return order


@router.patch("/{order_id}/status", response_model=OrderAdminOut)
async def change_status(
    order_id: int, body: OrderStatusUpdate, db: AsyncSession = Depends(get_db)
):
    try:
        return await order_service.set_status(db, order_id, body.status)
    except InvalidStatusTransition as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
