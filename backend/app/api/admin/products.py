"""Admin: kategoriya va mahsulot CRUD."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.admin.deps import get_current_admin
from app.core.database import get_db
from app.schemas.admin import (
    CategoryCreate,
    CategoryUpdate,
    ProductAdminOut,
    ProductCreate,
    ProductUpdate,
)
from app.schemas.catalog import CategoryOut
from app.services import catalog as catalog_service

router = APIRouter(tags=["admin-products"], dependencies=[Depends(get_current_admin)])


# ─────────────────── Kategoriyalar ───────────────────
@router.get("/categories", response_model=list[CategoryOut])
async def categories(db: AsyncSession = Depends(get_db)):
    return await catalog_service.list_categories(db, only_active=False)


@router.post("/categories", response_model=CategoryOut, status_code=201)
async def create_category(body: CategoryCreate, db: AsyncSession = Depends(get_db)):
    return await catalog_service.create_category(db, body.model_dump(exclude_none=True))


@router.patch("/categories/{category_id}", response_model=CategoryOut)
async def update_category(
    category_id: int, body: CategoryUpdate, db: AsyncSession = Depends(get_db)
):
    category = await catalog_service.update_category(
        db, category_id, body.model_dump(exclude_unset=True)
    )
    if category is None:
        raise HTTPException(status_code=404, detail="Kategoriya topilmadi")
    return category


# ─────────────────── Mahsulotlar ───────────────────
@router.get("/products", response_model=list[ProductAdminOut])
async def products(
    category_id: int | None = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    return await catalog_service.list_products(
        db, category_id=category_id, only_active=False, limit=limit, offset=offset
    )


@router.get("/products/{product_id}", response_model=ProductAdminOut)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    product = await catalog_service.get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
    return product


@router.post("/products", response_model=ProductAdminOut, status_code=201)
async def create_product(body: ProductCreate, db: AsyncSession = Depends(get_db)):
    return await catalog_service.create_product(db, body.model_dump())


@router.patch("/products/{product_id}", response_model=ProductAdminOut)
async def update_product(
    product_id: int, body: ProductUpdate, db: AsyncSession = Depends(get_db)
):
    product = await catalog_service.update_product(
        db, product_id, body.model_dump(exclude_unset=True)
    )
    if product is None:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
    return product


@router.delete("/products/{product_id}", status_code=204)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    ok = await catalog_service.delete_product(db, product_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
