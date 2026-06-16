"""Savat servisi — Redis'da (tez, sessiyaga bog'liq).

Tuzilma:  cart:{owner}  → Redis HASH  {product_id: qty}
`owner` — bot uchun telegram_id (website keyin o'z sessiya id'sini beradi).

MUHIM: savatda faqat product_id va qty saqlanadi — NARX EMAS. Narx har doim
checkout paytida bazadan olinadi (mijoz tomonga ishonilmaydi — xavfsizlik).
"""
from app.core.redis import redis_client

CART_TTL = 60 * 60 * 24 * 7  # 7 kun


def _key(owner: int | str) -> str:
    return f"cart:{owner}"


async def add_item(owner: int | str, product_id: int, qty: int = 1) -> int:
    """Savatga qo'shadi (mavjud bo'lsa miqdorini oshiradi). Yangi miqdorni qaytaradi."""
    key = _key(owner)
    new_qty = await redis_client.hincrby(key, str(product_id), qty)
    if new_qty <= 0:
        await redis_client.hdel(key, str(product_id))
        new_qty = 0
    await redis_client.expire(key, CART_TTL)
    return new_qty


async def set_qty(owner: int | str, product_id: int, qty: int) -> None:
    """Aniq miqdor o'rnatadi; qty<=0 bo'lsa o'chiradi."""
    key = _key(owner)
    if qty <= 0:
        await redis_client.hdel(key, str(product_id))
    else:
        await redis_client.hset(key, str(product_id), qty)
        await redis_client.expire(key, CART_TTL)


async def remove_item(owner: int | str, product_id: int) -> None:
    await redis_client.hdel(_key(owner), str(product_id))


async def get_items(owner: int | str) -> dict[int, int]:
    """{product_id: qty} qaytaradi."""
    raw = await redis_client.hgetall(_key(owner))
    return {int(pid): int(qty) for pid, qty in raw.items() if int(qty) > 0}


async def count(owner: int | str) -> int:
    """Savatdagi jami dona soni."""
    items = await get_items(owner)
    return sum(items.values())


async def clear(owner: int | str) -> None:
    await redis_client.delete(_key(owner))
