"""/start va ro'yxatdan o'tish (telefon) handlerlari.

1-bosqich oqimi:
  /start → mijoz bazada bormi? → yo'q bo'lsa telefon so'raladi (FSM)
        → kontakt yuborilsa mijoz yaratiladi → asosiy menyu ko'rsatiladi.
"""
from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Contact, Message
from sqlalchemy import select

from app.bot.keyboards.common import main_menu_kb, phone_request_kb
from app.bot.states import Registration
from app.core.database import SessionLocal
from app.models import Customer

router = Router(name="start")


async def _get_customer(telegram_id: int) -> Customer | None:
    async with SessionLocal() as session:
        result = await session.execute(
            select(Customer).where(Customer.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    customer = await _get_customer(message.from_user.id)

    if customer is None:
        await message.answer(
            "Assalomu alaykum! 💄 <b>MUSE BEAUTY</b> ga xush kelibsiz.\n\n"
            "Buyurtma berish uchun avval telefon raqamingizni ulashing.",
            reply_markup=phone_request_kb(),
        )
        await state.set_state(Registration.waiting_for_phone)
        return

    await message.answer(
        f"Xush kelibsiz, {customer.name or 'mijoz'}! 💖\n"
        "Quyidagi menyudan tanlang:",
        reply_markup=main_menu_kb(),
    )


@router.message(Registration.waiting_for_phone, F.contact)
async def receive_phone(message: Message, state: FSMContext) -> None:
    contact: Contact = message.contact

    # Boshqa odamning kontaktini yubormasin
    if contact.user_id and contact.user_id != message.from_user.id:
        await message.answer("Iltimos, o'zingizning raqamingizni ulashing 🙏")
        return

    async with SessionLocal() as session:
        existing = await session.execute(
            select(Customer).where(Customer.telegram_id == message.from_user.id)
        )
        customer = existing.scalar_one_or_none()
        if customer is None:
            customer = Customer(
                telegram_id=message.from_user.id,
                name=message.from_user.full_name,
                phone=contact.phone_number,
            )
            session.add(customer)
        else:
            customer.phone = contact.phone_number
        await session.commit()

    await state.clear()
    await message.answer(
        "Rahmat! Ro'yxatdan o'tdingiz ✅",
        reply_markup=main_menu_kb(),
    )


@router.message(Registration.waiting_for_phone)
async def phone_not_shared(message: Message) -> None:
    """Telefon o'rniga matn yuborilsa — tugmani bosishni eslatamiz."""
    await message.answer(
        "Iltimos, pastdagi <b>📱 Telefon raqamni ulashish</b> tugmasini bosing.",
        reply_markup=phone_request_kb(),
    )
