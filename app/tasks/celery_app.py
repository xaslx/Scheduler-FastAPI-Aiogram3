from celery import Celery

from config import settings

celery: Celery = Celery(
    'app.tasks',
    broker=f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}',
    include=['app.tasks.tasks'],
    broker_connection_retry_on_startup=True,
)
