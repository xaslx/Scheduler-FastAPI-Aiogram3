from redis.asyncio import Redis as aioredis
from redis import Redis
from config import settings


redis: Redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}", encoding="utf-8", decode_responses=True)