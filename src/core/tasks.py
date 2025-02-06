from celery import shared_task
from redis.asyncio import from_url 

@shared_task
async def async_task():
    redis = await from_url("redis://localhost")
    await redis.set("my_key", "my_value")
    value = await redis.get("my_key")
    await redis.close()
    return value
