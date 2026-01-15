from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth_router import router as auth_router
from app.api.users import router as users_router
from app.api.news import router as news_router
from app.api.comments import router as comments_router
from app.db import Base, engine
from app.redis_client import cache

# Создать таблицы если нужно (для dev)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lab1 News API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Добавляем роутеры
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(news_router)
app.include_router(comments_router)

@app.get("/")
def read_root():
    return {"message": "Lab1 News API with Auth and Redis Cache"}

@app.get("/health")
def health_check():
    """Проверка здоровья сервиса"""
    health_status = {
        "status": "healthy",
        "services": {}
    }
    
    try:
        redis_ok = cache.ping()
        health_status["services"]["redis"] = "healthy" if redis_ok else "unhealthy"
    except:
        health_status["services"]["redis"] = "unhealthy"
    
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        health_status["services"]["postgresql"] = "healthy"
    except:
        health_status["services"]["postgresql"] = "unhealthy"
    
    if any(status == "unhealthy" for status in health_status["services"].values()):
        health_status["status"] = "unhealthy"
    
    return health_status

@app.on_event("startup")
async def startup_event():
    """Проверяем соединения при старте"""
    try:
        if cache.ping():
            print("✓ Redis connected")
        else:
            print("✗ Redis connection failed")
    except Exception as e:
        print(f"✗ Redis connection error: {e}")