"""Joylashuv servisi — Google/Yandex map havolasidan koordinata ajratish.

Mijoz aniq manzilni 3 yo'l bilan yuborishi mumkin:
  1. Telegram lokatsiya (bot to'g'ridan latitude/longitude oladi — bu yerда parsing yo'q)
  2. Google Maps havolasi
  3. Yandex Maps havolasi (DIQQAT: Yandex `ll`/`pt` da tartib LNG,LAT)

Qisqa havolalar (maps.app.goo.gl, yandex.../-/...) HTTP redirect orqali ochiladi.
"""
import logging
import re

import httpx

logger = logging.getLogger("location")

_FLOAT = r"(-?\d{1,3}\.\d+)"


def _valid(lat: float, lng: float) -> bool:
    return -90.0 <= lat <= 90.0 and -180.0 <= lng <= 180.0


def _parse_google(url: str) -> tuple[float, float] | None:
    # place URL: !3d<lat>!4d<lng>
    m = re.search(rf"!3d{_FLOAT}!4d{_FLOAT}", url)
    if m:
        return float(m.group(1)), float(m.group(2))
    # /@<lat>,<lng>,zoom
    m = re.search(rf"@{_FLOAT},{_FLOAT}", url)
    if m:
        return float(m.group(1)), float(m.group(2))
    # ?q=<lat>,<lng>  yoki  q=loc:<lat>,<lng>  yoki  &ll=<lat>,<lng>
    m = re.search(rf"[?&](?:q|query|ll)=(?:loc:)?{_FLOAT},\s*{_FLOAT}", url)
    if m:
        return float(m.group(1)), float(m.group(2))
    return None


def _parse_yandex(url: str) -> tuple[float, float] | None:
    # Yandex: ll=<lng>,<lat>  yoki  pt=<lng>,<lat>  yoki  whatshere[point]=<lng>,<lat>
    m = re.search(rf"[?&](?:ll|pt)=(?:[^&]*?~)?{_FLOAT},\s*{_FLOAT}", url)
    if m:
        lng, lat = float(m.group(1)), float(m.group(2))  # tartib teskari!
        return lat, lng
    m = re.search(rf"point%5D={_FLOAT},{_FLOAT}", url)  # whatshere[point]=lng,lat
    if m:
        return float(m.group(2)), float(m.group(1))
    return None


def _parse_generic(text: str) -> tuple[float, float] | None:
    m = re.search(rf"geo:{_FLOAT},{_FLOAT}", text)
    if m:
        return float(m.group(1)), float(m.group(2))
    # Yalang'och "lat, lng" juftligi
    m = re.fullmatch(rf"\s*{_FLOAT},\s*{_FLOAT}\s*", text)
    if m:
        return float(m.group(1)), float(m.group(2))
    return None


def _parse(text: str) -> tuple[float, float] | None:
    low = text.lower()
    coords = None
    if "yandex" in low:
        coords = _parse_yandex(text)
    elif "google" in low or "goo.gl" in low:
        coords = _parse_google(text)
    if coords is None:
        # Ikkala formatni ham sinab ko'ramiz, keyin generic
        coords = _parse_google(text) or _parse_yandex(text) or _parse_generic(text)
    if coords and _valid(*coords):
        return coords
    return None


_SHORT = ("maps.app.goo.gl", "goo.gl/maps", "yandex.", "/-/", "maps.yandex")


async def extract_location(text: str) -> tuple[float, float] | None:
    """Havoladan (lat, lng). Qisqa havola bo'lsa redirect orqali ochib parsing qiladi."""
    text = text.strip()
    direct = _parse(text)
    if direct:
        return direct

    # Qisqa havola — redirectni kuzatib, final URL'ni parsing qilamiz
    if text.startswith("http") and any(s in text.lower() for s in _SHORT):
        try:
            async with httpx.AsyncClient(timeout=8, follow_redirects=True) as client:
                resp = await client.get(text)
                final = str(resp.url)
                return _parse(final)
        except httpx.HTTPError as exc:
            logger.warning("Qisqa havola ochilmadi: %s", exc)
            return None
    return None


# ─────────────────────── Xarita havolalari (admin/kuryer uchun) ───────────────────────
def google_link(lat, lng) -> str:
    return f"https://maps.google.com/?q={lat},{lng}"


def yandex_link(lat, lng) -> str:
    return f"https://yandex.uz/maps/?pt={lng},{lat}&z=17&l=map"
