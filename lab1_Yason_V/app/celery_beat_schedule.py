from celery.schedules import crontab
from .celery_app import celery_app

celery_app.conf.beat_schedule = {
    'weekly-digest': {
        'task': 'app.tasks.send_weekly_digest',
        'schedule': crontab(day_of_week=0, hour=9, minute=0),
    },
}