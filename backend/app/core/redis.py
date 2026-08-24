import redis
from app.core.config import get_settings

settings = get_settings()


def get_redis_client():
    return redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True,  # bytes ki jagah string milegi
    )


redis_client = get_redis_client()