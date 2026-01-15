from fastapi import FastAPI
from .api import users, news, comments
from .db import Base, engine
from .celery_app import celery_app
from .celery_beat_schedule import *

# Создать таблицы если нужно (для dev)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lab1 News API")

app.include_router(users.router)
app.include_router(news.router)
app.include_router(comments.router)
