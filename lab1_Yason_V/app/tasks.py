import logging
from celery.exceptions import Retry
from .celery_app import celery_app
from .db import SessionLocal
from . import crud
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_news_notification(self, news_id):
    try:
        db = SessionLocal()
        try:
            news = crud.get_news(db, news_id)
            if not news:
                logger.error(f"News {news_id} not found")
                return
            
            users = crud.list_users(db)
            
            for user in users:
                logger.info(f"Sent news notification to user {user.id} ({user.email}) about news: {news.title}")
                
            with open('notifications.log', 'a') as f:
                timestamp = datetime.now().isoformat()
                for user in users:
                    f.write(f"{timestamp} - NEWS_NOTIFICATION - User: {user.email}, News: {news.title}\n")
                    
        finally:
            db.close()
            
    except Exception as exc:
        logger.error(f"Failed to send news notification: {exc}")
        raise self.retry(countdown=2 ** self.request.retries, exc=exc)

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_weekly_digest(self):
    try:
        db = SessionLocal()
        try:
            week_ago = datetime.now() - timedelta(days=7)
            all_news = db.query(crud.models.News).all()
            recent_news = [n for n in all_news if n.published_at >= week_ago] if all_news else []
            
            logger.info(f"Found {len(recent_news)} recent news for digest")
            
            users = crud.list_users(db)
            
            for user in users:
                logger.info(f"Sent weekly digest to user {user.id} ({user.email}) with {len(recent_news)} news items")
                
            with open('digests.log', 'a') as f:
                timestamp = datetime.now().isoformat()
                for user in users:
                    f.write(f"{timestamp} - WEEKLY_DIGEST - User: {user.email}, News count: {len(recent_news)}\n")
                    
        finally:
            db.close()
            
    except Exception as exc:
        logger.error(f"Failed to send weekly digest: {exc}")
        raise self.retry(countdown=2 ** self.request.retries, exc=exc)