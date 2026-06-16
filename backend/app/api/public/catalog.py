"""Public katalog endpointlari (bot + website uchun, auth yo'q)."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.catalog import CategoryOut, ProductOut
from app.services import catalog as catalog_service

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/categories", response_model=list[CategoryOut])
async def categories(db: AsyncSession = Depends(get_db)):
    return await catalog_service.list_categories(db)


@router.get("/products", response_model=list[ProductOut])
async def products(
    category_id: int | None = None,
    q: str | None = Query(None, description="Nom bo'yicha qidiruv"),
    in_stock: bool = False,
    limit: int = Query(50, le=100),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    if q:
        return await catalog_service.search_products(db, q, limit=limit)
    return await catalog_service.list_products(
        db,
        category_id=category_id,
        only_in_stock=in_stock,
        limit=limit,
        offset=offset,
    )


@router.get("/products/{product_id}", response_model=ProductOut)
async def product(product_id: int, db: AsyncSession = Depends(get_db)):
    item = await catalog_service.get_product(db, product_id)
    if item is None or not item.is_active:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
    return item
