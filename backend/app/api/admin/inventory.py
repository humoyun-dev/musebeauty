"""Admin: ombor — ta'minot partiyasi kiritish (o'rtacha tannarx qayta hisoblanadi)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.admin.deps import get_current_admin
from app.core.database import get_db
from app.models import SupplyBatch
from app.schemas.admin import SupplyBatchCreate, SupplyBatchOut
from app.services import inventory as inventory_service
from app.services.inventory import ProductUnavailable

router = APIRouter(
    prefix="/supply-batches",
    tags=["admin-inventory"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("", response_model=list[SupplyBatchOut])
async def list_batches(limit: int = 100, db: AsyncSession = Depends(get_db)):
    stmt = select(SupplyBatch).order_by(SupplyBatch.id.desc()).limit(limit)
    return list((await db.execute(stmt)).scalars().all())


@router.post("", response_model=SupplyBatchOut, status_code=201)
async def receive_batch(body: SupplyBatchCreate, db: AsyncSession = Depends(get_db)):
    try:
        batch = await inventory_service.receive_supply_batch(
            db,
            supplier=body.supplier,
            arrival_date=body.arrival_date,
            note=body.note,
            items=[item.model_dump() for item in body.items],
        )
    except ProductUnavailable as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return batch
