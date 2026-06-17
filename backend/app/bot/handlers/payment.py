"""To'lov cheki handleri — checkout'dan keyin mijoz rasm yuboradi."""
from decimal import Decimal

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.bot.keyboards.common import main_menu_kb
from app.bot.states import Checkout
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.utils import format_money
from app.services import payment as payment_service

router = Router(name="payment")


@router.message(Checkout.sending_receipt, F.photo)
async def receive_receipt(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    order_id = data.get("order_id")
    amount = Decimal(data.get("amount", "0"))
    # Eng katta o'lchamdagi rasmni olamiz (file_id saqlaymiz — admin keyin ko'radi)
    file_id = message.photo[-1].file_id

    async with SessionLocal() as session:
        await payment_service.submit_receipt(
            session,
            order_id=order_id,
            amount=amount,
            screenshot_url=file_id,
        )

    await state.clear()
    await message.answer(
        f"✅ Chek qabul qilindi! Buyurtma #{order_id}\n\n"
        "Admin to'lovni tekshirib tasdiqlaydi — keyin sizga xabar beramiz 💌",
        reply_markup=main_menu_kb(),
    )

    # Adminlarga chek rasmini yuboramiz
    for admin_id in settings.admin_ids:
        try:
            await message.bot.send_photo(
                admin_id,
                photo=file_id,
                caption=(
                    f"🧾 <b>Buyurtma #{order_id}</b> uchun chek keldi\n"
                    f"Summa: {format_money(amount)}\n"
                    "Tasdiqlash uchun admin panelga kiring."
                ),
            )
        except Exception:
            pass


@router.message(Checkout.sending_receipt)
async def receipt_not_photo(message: Message) -> None:
    await message.answer("Iltimos, to'lov <b>chekining rasmini</b> yuboring 📸")
