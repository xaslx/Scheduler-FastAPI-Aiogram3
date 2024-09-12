from redis import Redis
from redis.asyncio import Redis as aioredis

from config import settings

redis: Redis = aioredis.from_url(
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    encoding="utf-8",
    decode_responses=True,
)
