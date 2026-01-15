from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, crud, deps
from ..deps import get_db, get_current_author_or_admin_user, check_news_permission, get_current_user

router = APIRouter(prefix="/news", tags=["news"])

@router.post("/", response_model=schemas.NewsRead)
def create_news(
    news_in: schemas.NewsCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_author_or_admin_user)
):
    return crud.create_news(db, news_in, author_id=current_user.id)

@router.get("/{news_id}", response_model=schemas.NewsRead)
def read_news(
    news_id: int,
    db: Session = Depends(get_db)
):
    n = crud.get_news(db, news_id)
    if not n:
        raise HTTPException(404, "News not found")
    return n

# Функция для получения новости с проверкой прав
def get_news_with_permission_check(news_id: int, db: Session, current_user):
    """Вспомогательная функция для проверки прав на новость"""
    return check_news_permission(news_id, db, current_user)

@router.patch("/{news_id}", response_model=schemas.NewsRead)
def update_news(
    news_id: int,
    news_in: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Получаем новость с проверкой прав
    news_obj = check_news_permission(news_id, db, current_user)
    return crud.update_news(db, news_obj, news_in)

@router.delete("/{news_id}")
def delete_news(
    news_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Получаем новость с проверкой прав
    news_obj = check_news_permission(news_id, db, current_user)
    crud.delete_news(db, news_obj)
    return {"ok": True}