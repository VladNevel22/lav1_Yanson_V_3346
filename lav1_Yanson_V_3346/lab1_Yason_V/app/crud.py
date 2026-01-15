from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from . import models, schemas, auth

# USERS
def create_user(db: Session, user_in: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user_in.password)
    user = models.User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_oauth_user(db: Session, user_in: schemas.UserOAuthCreate):
    user = models.User(
        name=user_in.name,
        email=user_in.email,
        github_id=user_in.github_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_github_id(db: Session, github_id: str):
    return db.query(models.User).filter(models.User.github_id == github_id).first()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def list_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def update_user(db: Session, user_id: int, data: dict):
    user = get_user(db, user_id)
    if not user:
        return None
    
    for key, value in data.items():
        if key == "password" and value:
            value = auth.get_password_hash(value)
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user

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
    for k, v in data.items():
        setattr(news_obj, k, v)
    db.add(news_obj)
    db.commit()
    db.refresh(news_obj)
    return news_obj

def delete_news(db: Session, news_obj):
    db.delete(news_obj)
    db.commit()

# COMMENTS
def create_comment(db: Session, comment_in: schemas.CommentCreate, author_id: int):
    comment = models.Comment(**comment_in.dict(), author_id=author_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

def get_comment(db: Session, comment_id: int):
    return db.query(models.Comment).filter(models.Comment.id == comment_id).first()

def update_comment(db: Session, comment_obj, data: dict):
    for k, v in data.items():
        setattr(comment_obj, k, v)
    db.add(comment_obj)
    db.commit()
    db.refresh(comment_obj)
    return comment_obj

def delete_comment(db: Session, comment_obj):
    db.delete(comment_obj)
    db.commit()

# REFRESH SESSIONS
def create_refresh_session(db: Session, user_id: int, refresh_token: str, user_agent: str = None):
    expires_at = datetime.utcnow() + timedelta(days=7)
    session = models.RefreshSession(
        user_id=user_id,
        refresh_token=refresh_token,
        user_agent=user_agent,
        expires_at=expires_at
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def get_refresh_session(db: Session, refresh_token: str):
    return db.query(models.RefreshSession).filter(
        models.RefreshSession.refresh_token == refresh_token
    ).first()

def delete_refresh_session(db: Session, refresh_token: str):
    session = get_refresh_session(db, refresh_token)
    if session:
        db.delete(session)
        db.commit()

def delete_all_user_sessions(db: Session, user_id: int):
    db.query(models.RefreshSession).filter(
        models.RefreshSession.user_id == user_id
    ).delete()
    db.commit()

def get_user_sessions(db: Session, user_id: int):
    return db.query(models.RefreshSession).filter(
        models.RefreshSession.user_id == user_id
    ).all()