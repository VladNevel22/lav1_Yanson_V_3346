# Lab1 News API

FastAPI приложение для новостного портала.

## Запуск

1. Запустите базу данных:
```bash
docker-compose up -d

pip install -r requirements.txt

# Запуск FastAPI
uvicorn app.main:app --reload

# Запуск Celery worker
celery -A app.celery_app worker --loglevel=info

# Запуск Celery beat
celery -A app.celery_app beat --loglevel=info




