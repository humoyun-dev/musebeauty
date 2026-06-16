"""Bot FSM holatlari (Redis'da saqlanadi).

1-bosqich: faqat ro'yxatdan o'tish (telefon). Checkout FSM (tuman → manzil →
tasdiq) 2-bosqichda shu yerga qo'shiladi.
"""
from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    waiting_for_phone = State()


class Checkout(StatesGroup):
    choosing_district = State()
    entering_address = State()
    entering_promo = State()      # 4-bosqich: ixtiyoriy promokod
    confirming = State()
    sending_receipt = State()
