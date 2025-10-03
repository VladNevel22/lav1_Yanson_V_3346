from fastapi import FastAPI
from .api import users, news, comments
from .db import Base, engine

# Создать таблицы если нужно (для dev)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lab1 News API")

app.include_router(users.router)
app.include_router(news.router)
app.include_router(comments.router)
