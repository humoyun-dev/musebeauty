"""Admin: chegirma (discounts) va promokod (promo_codes) CRUD."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.admin.deps import get_current_admin
from app.core.database import get_db
from app.schemas.admin import (
    DiscountIn,
    DiscountOut,
    DiscountUpdate,
    PromoIn,
    PromoOut,
    PromoUpdate,
)
from app.services import marketing as mkt

router = APIRouter(tags=["admin-marketing"], dependencies=[Depends(get_current_admin)])


# ─────────────────── Chegirmalar ───────────────────
@router.get("/discounts", response_model=list[DiscountOut])
async def discounts(db: AsyncSession = Depends(get_db)):
    return await mkt.list_discounts(db)


@router.post("/discounts", response_model=DiscountOut, status_code=201)
async def create_discount(body: DiscountIn, db: AsyncSession = Depends(get_db)):
    return await mkt.create_discount(db, body.model_dump())


@router.patch("/discounts/{discount_id}", response_model=DiscountOut)
async def update_discount(discount_id: int, body: DiscountUpdate, db: AsyncSession = Depends(get_db)):
    obj = await mkt.update_discount(db, discount_id, body.model_dump(exclude_unset=True))
    if obj is None:
        raise HTTPException(status_code=404, detail="Chegirma topilmadi")
    return obj


@router.delete("/discounts/{discount_id}", status_code=204)
async def delete_discount(discount_id: int, db: AsyncSession = Depends(get_db)):
    if not await mkt.delete_discount(db, discount_id):
        raise HTTPException(status_code=404, detail="Chegirma topilmadi")


# ─────────────────── Promokodlar ───────────────────
@router.get("/promo-codes", response_model=list[PromoOut])
async def promos(db: AsyncSession = Depends(get_db)):
    return await mkt.list_promos(db)


@router.post("/promo-codes", response_model=PromoOut, status_code=201)
async def create_promo(body: PromoIn, db: AsyncSession = Depends(get_db)):
    return await mkt.create_promo(db, body.model_dump())


@router.patch("/promo-codes/{promo_id}", response_model=PromoOut)
async def update_promo(promo_id: int, body: PromoUpdate, db: AsyncSession = Depends(get_db)):
    obj = await mkt.update_promo(db, promo_id, body.model_dump(exclude_unset=True))
    if obj is None:
        raise HTTPException(status_code=404, detail="Promokod topilmadi")
    return obj


@router.delete("/promo-codes/{promo_id}", status_code=204)
async def delete_promo(promo_id: int, db: AsyncSession = Depends(get_db)):
    if not await mkt.delete_promo(db, promo_id):
        raise HTTPException(status_code=404, detail="Promokod topilmadi")
