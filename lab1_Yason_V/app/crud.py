from sqlalchemy.orm import Session
from . import models, schemas

# USERS
def create_user(db: Session, user_in: schemas.UserCreate):
    user = models.User(**user_in.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def list_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

# NEWS
def create_news(db: Session, news_in: schemas.NewsCreate, author_id: int):
    news = models.News(**news_in.dict(), author_id=author_id)
    db.add(news)
    db.commit()
    db.refresh(news)
    return news

def get_news(db: Session, news_id: int):
    return db.query(models.News).filter(models.News.id == news_id).first()

def update_news(db: Session, news_obj, data: dict):
    for k,v in data.items():
        setattr(news_obj, k, v)
    db.add(news_obj)
    db.commit()
    db.refresh(news_obj)
    return news_obj

def delete_news(db: Session, news_obj):
    db.delete(news_obj)
    db.commit()

# COMMENTS
def create_comment(db: Session, comment_in: schemas.CommentCreate):
    comment = models.Comment(**comment_in.dict())
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

def get_comment(db: Session, comment_id: int):
    return db.query(models.Comment).filter(models.Comment.id == comment_id).first()

def update_comment(db: Session, comment_obj, data: dict):
    for k,v in data.items():
        setattr(comment_obj, k, v)
    db.add(comment_obj)
    db.commit()
    db.refresh(comment_obj)
    return comment_obj

def delete_comment(db: Session, comment_obj):
    db.delete(comment_obj)
    db.commit()
