"""Public aksiyalar — faol chegirma va promokodlar (bot + website ko'rsatadi)."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.promotions import PromotionsOut
from app.services import pricing as pricing_service
from app.services import promo as promo_service

router = APIRouter(prefix="/promotions", tags=["promotions"])


@router.get("", response_model=PromotionsOut)
async def promotions(db: AsyncSession = Depends(get_db)):
    discounts = await pricing_service.list_active_discounts(db)
    promos = await promo_service.list_active_promos(db)
    return PromotionsOut(discounts=discounts, promo_codes=promos)
