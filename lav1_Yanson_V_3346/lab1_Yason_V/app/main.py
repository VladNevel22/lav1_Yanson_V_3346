from fastapi import FastAPI
from app.api import users, news, comments, auth_router
from app.db import Base, engine

# Создать таблицы если нужно (для dev)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lab1 News API")

app.include_router(auth_router.router)
app.include_router(users.router)
app.include_router(news.router)
app.include_router(comments.router)

@app.get("/")
def read_root():
    return {"message": "Lab1 News API with Auth"}