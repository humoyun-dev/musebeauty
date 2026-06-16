"""Public buyurtma endpointlari — tumanlar ro'yxati va buyurtma yaratish.

Bot bilan bir xil order/inventory/pricing servislarini chaqiradi.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models import Customer, District
from app.schemas.order import (
    DistrictOut,
    OrderCreateIn,
    OrderOut,
    QuoteIn,
    QuoteOut,
    WebOrderIn,
    WebOrderOut,
)
from app.services import customer as customer_service
from app.services import location as location_service
from app.services import order as order_service
from app.services import payme as payme_service
from app.services import pricing as pricing_service
from app.services.inventory import InsufficientStock, ProductUnavailable
from app.services.order import EmptyCart
from app.services.promo import PromoError

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/districts", response_model=list[DistrictOut])
async def districts(db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(District).order_by(District.name))).scalars().all()
    return list(rows)


@router.post("", response_model=OrderOut, status_code=201)
async def create_order(body: OrderCreateIn, db: AsyncSession = Depends(get_db)):
    customer = (
        await db.execute(select(Customer).where(Customer.telegram_id == body.telegram_id))
    ).scalar_one_or_none()
    if customer is None:
        raise HTTPException(status_code=404, detail="Mijoz topilmadi (avval botda ro'yxatdan o'ting)")

    items = {item.product_id: item.qty for item in body.items}
    try:
        order = await order_service.create_order_from_cart(
            db,
            customer=customer,
            items=items,
            district_id=body.district_id,
            address=body.address,
            phone=body.phone or customer.phone,
            promo_code=body.promo_code,
        )
    except EmptyCart:
        raise HTTPException(status_code=400, detail="Savat bo'sh")
    except InsufficientStock as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except ProductUnavailable as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except PromoError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return await order_service.get_order(db, order.id)


@router.post("/quote", response_model=QuoteOut)
async def quote(body: QuoteIn, db: AsyncSession = Depends(get_db)):
    """Narx oldindan ko'rish (website savatda chegirma/promokod/yetkazib berishni ko'rsatadi)."""
    items = {it.product_id: it.qty for it in body.items}
    # Telefon berilsa, mavjud mijozni topamiz (promokod per-user/first-order uchun)
    customer = None
    if body.phone:
        customer = (
            await db.execute(select(Customer).where(Customer.phone == body.phone.strip()))
        ).scalars().first()
    q, promo_error = await pricing_service.quote(
        db, items, body.district_id, customer=customer, promo_code=body.promo_code
    )
    return QuoteOut(
        lines=[
            {
                "product_id": ln.product_id,
                "name": ln.name,
                "qty": ln.qty,
                "unit_price": ln.unit_price,
                "line_total": ln.line_total,
            }
            for ln in q.lines
        ],
        subtotal=q.subtotal,
        discount_amount=q.discount_amount,
        delivery_fee=q.delivery_fee,
        free_delivery=q.free_delivery,
        total=q.total,
        promo_error=promo_error,
    )


@router.post("/web", response_model=WebOrderOut, status_code=201)
async def create_web_order(body: WebOrderIn, db: AsyncSession = Depends(get_db)):
    """Website checkout (Telegram'siz) — telefon orqali mijoz topiladi/yaratiladi."""
    customer = await customer_service.get_or_create_web_customer(
        db, name=body.name, phone=body.phone
    )
    items = {it.product_id: it.qty for it in body.items}

    # Joylashuv: to'g'ridan lat/lng, yoki map havoladan parse
    lat, lng = body.latitude, body.longitude
    if (lat is None or lng is None) and body.map_link:
        coords = await location_service.extract_location(body.map_link)
        if coords:
            lat, lng = coords

    try:
        order = await order_service.create_order_from_cart(
            db,
            customer=customer,
            items=items,
            district_id=body.district_id,
            address=body.address,
            phone=body.phone,
            promo_code=body.promo_code,
            latitude=lat,
            longitude=lng,
        )
    except EmptyCart:
        raise HTTPException(status_code=400, detail="Savat bo'sh")
    except (InsufficientStock, ProductUnavailable) as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except PromoError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    payme_url = None
    if settings.payme_enabled and settings.payme_merchant_id:
        payme_url = payme_service.checkout_url(order.id, int(order.total * 100))

    return WebOrderOut(
        order_id=order.id,
        total=order.total,
        status=order.status,
        payment_card_number=settings.payment_card_number,
        payment_card_holder=settings.payment_card_holder,
        payme_url=payme_url,
    )


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    order = await order_service.get_order(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
    return order
