"""Public savat endpointlari — website uchun (bot Redis savatdan to'g'ridan foydalanadi).

`owner` — savat egasi identifikatori (website sessiya id yoki telegram_id).
Bot bilan bir xil cart servisni ishlatadi (Redis), mantiq takrorlanmaydi.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.cart import CartItemIn, CartLineOut, CartOut
from app.services import cart as cart_service
from app.services import catalog as catalog_service

router = APIRouter(prefix="/cart", tags=["cart"])


async def _build_cart(owner: str, db: AsyncSession) -> CartOut:
    items = await cart_service.get_items(owner)
    lines: list[CartLineOut] = []
    subtotal = 0
    for pid, qty in items.items():
        product = await catalog_service.get_product(db, pid)
        if product is None:
            await cart_service.remove_item(owner, pid)
            continue
        line_total = product.price * qty
        subtotal += line_total
        lines.append(
            CartLineOut(
                product_id=pid,
                name=product.name,
                qty=qty,
                unit_price=product.price,
                line_total=line_total,
            )
        )
    return CartOut(lines=lines, subtotal=subtotal, item_count=sum(i.qty for i in lines))


@router.get("/{owner}", response_model=CartOut)
async def get_cart(owner: str, db: AsyncSession = Depends(get_db)):
    return await _build_cart(owner, db)


@router.post("/{owner}/items", response_model=CartOut)
async def add_item(owner: str, body: CartItemIn, db: AsyncSession = Depends(get_db)):
    await cart_service.add_item(owner, body.product_id, body.qty)
    return await _build_cart(owner, db)


@router.delete("/{owner}/items/{product_id}", response_model=CartOut)
async def remove_item(owner: str, product_id: int, db: AsyncSession = Depends(get_db)):
    await cart_service.remove_item(owner, product_id)
    return await _build_cart(owner, db)


@router.delete("/{owner}", status_code=204)
async def clear_cart(owner: str):
    await cart_service.clear(owner)
