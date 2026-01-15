from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, crud
from ..deps import get_db, get_current_author_or_admin_user, check_news_permission, get_current_user
from ..cache_service import cache_service

router = APIRouter(prefix="/news", tags=["news"])

@router.post("/", response_model=schemas.NewsRead)

def create_news(
    news_in: schemas.NewsCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_author_or_admin_user)
):
    news = crud.create_news(db, news_in, author_id=current_user.id)
    return news

@router.get("/{news_id}", response_model=schemas.NewsRead)
def read_news(
    news_id: int,
    db: Session = Depends(get_db)
):

    cached_news = cache_service.get_news(news_id)
    if cached_news:
        cached_news['published_at'] = datetime.fromisoformat(cached_news['published_at'])
        return cached_news
    

    news = crud.get_news(db, news_id)
    if not news:
        raise HTTPException(404, "News not found")
    
    news_dict = {
        'id': news.id,
        'title': news.title,
        'content': news.content,
        'published_at': news.published_at.isoformat() if news.published_at else None,
        'author_id': news.author_id,
        'cover': news.cover
    }

    cache_service.set_news(news_id, news_dict)
    
    return news

@router.patch("/{news_id}", response_model=schemas.NewsRead)
def update_news(
    news_id: int,
    news_in: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    news_obj = check_news_permission(news_id, db, current_user)
    updated_news = crud.update_news(db, news_obj, news_in)
    news_dict = {
        'id': updated_news.id,
        'title': updated_news.title,
        'content': updated_news.content,
        'published_at': updated_news.published_at.isoformat() if updated_news.published_at else None,
        'author_id': updated_news.author_id,
        'cover': updated_news.cover
    }
    cache_service.set_news(news_id, news_dict)
    
    return updated_news

@router.delete("/{news_id}")
def delete_news(
    news_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    news_obj = check_news_permission(news_id, db, current_user)
    crud.delete_news(db, news_obj)
    
    cache_service.delete_news(news_id)
    
    return {"ok": True}