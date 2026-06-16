"""Checkout FSM: tuman → manzil → (ixtiyoriy) promokod → tasdiq → buyurtma → to'lov."""
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardRemove,
)
from sqlalchemy import select

from app.bot.keyboards.cart import confirm_kb, districts_kb
from app.bot.keyboards.common import location_request_kb
from app.bot.states import Checkout
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.utils import format_money
from app.models import Customer, District
from app.services import cart as cart_service
from app.services import location as location_service
from app.services import notify as notify_service
from app.services import order as order_service
from app.services import pricing as pricing_service
from app.services.inventory import InsufficientStock, ProductUnavailable
from app.services.promo import PromoError

router = Router(name="checkout")


def _skip_promo_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➡️ Promokodsiz davom etish", callback_data="promo:skip")]
        ]
    )


async def _get_customer(telegram_id: int) -> Customer | None:
    async with SessionLocal() as session:
        return (
            await session.execute(
                select(Customer).where(Customer.telegram_id == telegram_id)
            )
        ).scalar_one_or_none()


@router.callback_query(F.data == "checkout")
async def start_checkout(call: CallbackQuery, state: FSMContext) -> None:
    items = await cart_service.get_items(call.from_user.id)
    if not items:
        await call.answer("Savatingiz bo'sh", show_alert=True)
        return
    customer = await _get_customer(call.from_user.id)
    if customer is None:
        await call.answer("Avval /start orqali ro'yxatdan o'ting", show_alert=True)
        return

    async with SessionLocal() as session:
        districts = list(
            (await session.execute(select(District).order_by(District.name))).scalars().all()
        )
    if not districts:
        await call.answer("Yetkazib berish tumanlari sozlanmagan", show_alert=True)
        return

    await state.set_state(Checkout.choosing_district)
    await call.message.answer("🚚 Qaysi tumanga yetkazamiz?", reply_markup=districts_kb(districts))
    await call.answer()


@router.callback_query(Checkout.choosing_district, F.data.startswith("dist:"))
async def choose_district(call: CallbackQuery, state: FSMContext) -> None:
    district_id = int(call.data.split(":")[1])
    await state.update_data(district_id=district_id)
    await state.set_state(Checkout.entering_address)
    await call.message.edit_text("🚚 Tuman tanlandi.")
    await call.message.answer(
        "🏠 <b>Manzilingizni yuboring</b> — quyidagilardan biri bilan:\n\n"
        "📍 <b>Joylashuvni yuborish</b> tugmasi (eng aniq)\n"
        "🔗 Google yoki Yandex Maps havolasi\n"
        "✍️ yoki manzilni matn bilan yozing (ko'cha, uy, mo'ljal)",
        reply_markup=location_request_kb(),
    )
    await call.answer()


async def _finish_address(message: Message, state: FSMContext, address: str) -> None:
    await state.update_data(address=address)
    await state.set_state(Checkout.entering_promo)
    await message.answer(
        "🎁 Promokodingiz bo'lsa kiriting (yoki tugmani bosing):",
        reply_markup=_skip_promo_kb(),
    )


@router.message(Checkout.entering_address, F.location)
async def address_via_location(message: Message, state: FSMContext) -> None:
    """Telegram lokatsiya — aniq koordinata."""
    loc = message.location
    await state.update_data(lat=loc.latitude, lng=loc.longitude)
    await message.answer(
        "✅ Joylashuv qabul qilindi!\n"
        "Endi uy/kvartira/mo'ljalni yozing (yoki «-» yuboring):",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(Checkout.entering_address, F.text)
async def enter_address(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    data = await state.get_data()
    has_coords = data.get("lat") is not None

    # 1) Map havola (Google/Yandex)?
    if text.startswith("http"):
        coords = await location_service.extract_location(text)
        if coords:
            await state.update_data(lat=coords[0], lng=coords[1])
            await message.answer(
                "✅ Joylashuv aniqlandi!\nUy/kvartira/mo'ljalni yozing (yoki «-»):",
                reply_markup=ReplyKeyboardRemove(),
            )
            return
        await message.answer(
            "🤔 Havoladan joyni aniqlay olmadim. Manzilni matn bilan yozing "
            "yoki 📍 <b>Joylashuvni yuborish</b> tugmasidan foydalaning.",
            reply_markup=location_request_kb(),
        )
        return

    # 2) «-» / «yo'q» — koordinata bor bo'lsa manzilsiz davom etamiz
    if text.lower() in {"-", "yoq", "yo'q", "yoʻq", "yoq"}:
        if has_coords:
            await _finish_address(message, state, "(joylashuv bo'yicha)")
        else:
            await message.answer("Manzil kerak. Iltimos yozing yoki 📍 joylashuv yuboring.")
        return

    # 3) Matn manzil
    if len(text) < 5 and not has_coords:
        await message.answer("Manzil juda qisqa. To'liqroq yozing 🙏")
        return
    await _finish_address(message, state, text)


async def _send_summary(target: Message, *, user_id: int, state: FSMContext) -> None:
    """Narx xulosasini (promokod bilan/siz) chiqaradi va tasdiqlash so'raydi."""
    data = await state.get_data()
    items = await cart_service.get_items(user_id)
    customer = await _get_customer(user_id)
    promo_code = data.get("promo_code")

    async with SessionLocal() as session:
        quote, _ = await pricing_service.quote(
            session, items, data.get("district_id"),
            customer=customer, promo_code=promo_code,
        )
        district = await session.get(District, data["district_id"]) if data.get("district_id") else None

    lines = "\n".join(
        f"• {ln.name} — {ln.qty} × {format_money(ln.unit_price)} = {format_money(ln.line_total)}"
        for ln in quote.lines
    )
    parts = [
        "🧾 <b>Buyurtma xulosasi</b>\n",
        lines,
        f"\nMahsulotlar: {format_money(quote.subtotal)}",
    ]
    if quote.discount_amount > 0:
        label = "Promokod" if quote.discount_source == "promo" else "Chegirma"
        parts.append(f"{label}: −{format_money(quote.discount_amount)}")
    if quote.free_delivery:
        parts.append("Yetkazib berish: <s>bor</s> <b>BEPUL</b> 🎉")
    else:
        parts.append(
            f"Yetkazib berish ({district.name if district else '-'}): {format_money(quote.delivery_fee)}"
        )
    parts.append(f"<b>Jami: {format_money(quote.total)}</b>")
    parts.append(f"\n📍 Manzil: {data.get('address')}")
    if data.get("lat") is not None:
        parts.append("🗺 Joylashuv: yuborilgan ✅")
    parts.append(f"📱 Telefon: {customer.phone if customer else '-'}")
    parts.append("\nTasdiqlaysizmi?")

    await state.set_state(Checkout.confirming)
    await target.answer("\n".join(parts), reply_markup=confirm_kb())


@router.message(Checkout.entering_promo, F.text)
async def enter_promo(message: Message, state: FSMContext) -> None:
    code = message.text.strip()
    data = await state.get_data()
    items = await cart_service.get_items(message.from_user.id)
    customer = await _get_customer(message.from_user.id)

    # Promokodni tekshiramiz (xato bo'lsa sababi promo_error'da keladi)
    async with SessionLocal() as session:
        _, promo_error = await pricing_service.quote(
            session, items, data.get("district_id"),
            customer=customer, promo_code=code,
        )
    if promo_error:
        await message.answer(f"❌ {promo_error}\n\nBoshqa kod kiriting yoki tugmani bosing:", reply_markup=_skip_promo_kb())
        return

    await state.update_data(promo_code=code)
    await message.answer("✅ Promokod qabul qilindi!")
    await _send_summary(message, user_id=message.from_user.id, state=state)


@router.callback_query(Checkout.entering_promo, F.data == "promo:skip")
async def skip_promo(call: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(promo_code=None)
    await _send_summary(call.message, user_id=call.from_user.id, state=state)
    await call.answer()


@router.callback_query(Checkout.confirming, F.data == "checkout:confirm")
async def confirm_order(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    items = await cart_service.get_items(call.from_user.id)
    customer = await _get_customer(call.from_user.id)
    if not items or customer is None:
        await state.clear()
        await call.answer("Buyurtma berib bo'lmadi", show_alert=True)
        return

    async with SessionLocal() as session:
        try:
            order = await order_service.create_order_from_cart(
                session,
                customer=customer,
                items=items,
                district_id=data.get("district_id"),
                address=data.get("address"),
                phone=customer.phone,
                promo_code=data.get("promo_code"),
                latitude=data.get("lat"),
                longitude=data.get("lng"),
            )
        except InsufficientStock as exc:
            await call.answer(str(exc), show_alert=True)
            return
        except ProductUnavailable:
            await call.answer("Ba'zi mahsulotlar mavjud emas. Savatni yangilang.", show_alert=True)
            return
        except PromoError as exc:
            # Promokod oxirgi lahzada yaroqsiz bo'ldi — kodsiz qayta ko'rsatamiz
            await state.update_data(promo_code=None)
            await call.answer(f"Promokod: {exc}", show_alert=True)
            await _send_summary(call.message, user_id=call.from_user.id, state=state)
            return

    await cart_service.clear(call.from_user.id)
    await state.set_state(Checkout.sending_receipt)
    await state.update_data(order_id=order.id, amount=str(order.total))

    await call.message.answer(
        f"✅ <b>Buyurtma #{order.id} qabul qilindi!</b>\n\n"
        f"To'lov uchun: <b>{format_money(order.total)}</b>\n"
        f"💳 Karta: <code>{settings.payment_card_number}</code>\n"
        f"👤 {settings.payment_card_holder}\n\n"
        "To'lovni amalga oshirib, <b>chek/screenshot rasmini</b> shu yerga yuboring 📸"
    )
    await call.answer()

    map_line = ""
    if data.get("lat") is not None:
        g = location_service.google_link(data["lat"], data["lng"])
        y = location_service.yandex_link(data["lat"], data["lng"])
        map_line = f"🗺 <a href='{g}'>Google</a> | <a href='{y}'>Yandex</a>\n"
    await notify_service.notify_admins(
        f"🆕 <b>Yangi buyurtma #{order.id}</b>\n"
        f"Mijoz: {customer.name or '-'} ({customer.phone or '-'})\n"
        f"Summa: {format_money(order.total)}\n"
        f"Manzil: {data.get('address')}\n"
        f"{map_line}"
        f"⏳ To'lov cheki kutilmoqda"
    )


@router.callback_query(F.data == "checkout:cancel")
async def cancel_checkout(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.edit_text("❌ Buyurtma bekor qilindi. Savatingiz saqlanib qoldi.")
    await call.answer()
