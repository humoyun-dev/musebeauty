"""Async Redis klient — bot FSM, savat va kesh uchun yagona ulanish.

decode_responses=True — qiymatlar str bo'lib qaytadi (byte emas).
"""
from redis.asyncio import Redis, from_url

from app.core.config import settings

redis_client: Redis = from_url(
    settings.redis_url,
    decode_responses=True,
    health_check_interval=30,
)
