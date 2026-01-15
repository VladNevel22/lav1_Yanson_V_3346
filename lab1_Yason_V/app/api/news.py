from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, crud, models
from ..deps import get_db, get_current_user
from ..tasks import send_news_notification

router = APIRouter(prefix="/news", tags=["news"])

@router.post("/", response_model=schemas.NewsRead)
def create_news(news_in: schemas.NewsCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if not current_user.is_author:
        raise HTTPException(403, "User is not verified as author")
    news = crud.create_news(db, news_in, author_id=current_user.id)
    
    send_news_notification.delay(news.id)
    
    return news

@router.get("/{news_id}", response_model=schemas.NewsRead)
def read_news(news_id: int, db: Session = Depends(get_db)):
    n = crud.get_news(db, news_id)
    if not n:
        raise HTTPException(404, "News not found")
    return n

@router.patch("/{news_id}", response_model=schemas.NewsRead)
def update_news(news_id: int, news_in: dict, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    n = crud.get_news(db, news_id)
    if not n:
        raise HTTPException(404, "News not found")
    if n.author_id != current_user.id:
        raise HTTPException(403, "Only author can update")
    return crud.update_news(db, n, news_in)

@router.delete("/{news_id}")
def delete_news(news_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    n = crud.get_news(db, news_id)
    if not n:
        raise HTTPException(404, "News not found")
    if n.author_id != current_user.id:
        raise HTTPException(403, "Only author can delete")
    crud.delete_news(db, n)
    return {"ok": True}
