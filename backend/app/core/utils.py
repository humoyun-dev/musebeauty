"""Kichik umumiy yordamchilar."""
from decimal import Decimal


def format_money(amount: Decimal | int | float) -> str:
    """Pulni o'qishga qulay ko'rinishda: 1250000 → '1 250 000 so'm'.

    So'm butun ishlatilgani uchun kasr qismi tashlanadi.
    """
    value = int(Decimal(amount))
    # Mingliklarni bo'sh joy bilan ajratamiz (1 250 000)
    formatted = f"{value:,}".replace(",", " ")
    return f"{formatted} so'm"
