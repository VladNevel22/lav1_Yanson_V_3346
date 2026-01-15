from celery import Celery
import os

celery_app = Celery(
    'lab1_news',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Moscow',
    enable_utc=True,
    imports=['app.tasks']
)

celery_app.conf.beat_schedule = {
    'weekly-digest': {
        'task': 'app.tasks.send_weekly_digest',
        'schedule': 60.0, 
    },
}