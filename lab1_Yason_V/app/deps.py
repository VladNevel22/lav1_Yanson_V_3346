from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError
from .db import SessionLocal
from . import crud, auth
from .cache_service import cache_service

security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = auth.decode_token(token)
    
    if payload is None or payload.get("type") != "access":
        raise credentials_exception
    
    user_id: int = payload.get("user_id")
    if user_id is None:
        raise credentials_exception
    

    cached_user = cache_service.get_user(user_id)
    if cached_user:
        from .models import User
        user = User(
            id=cached_user['id'],
            name=cached_user['name'],
            email=cached_user['email'],
            is_author=cached_user['is_author'],
            is_admin=cached_user['is_admin'],
            avatar=cached_user['avatar'],
            github_id=cached_user['github_id']
        )
        return user
    
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise credentials_exception
    

    cache_service.set_user(user)
    
    return user

def get_current_admin_user(current_user = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

def get_current_author_or_admin_user(current_user = Depends(get_current_user)):
    if not current_user.is_author and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not verified as author"
        )
    return current_user

# Dependency для проверки прав на новость
def check_news_permission(
    news_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    news = crud.get_news(db, news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    if news.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return news

# Dependency для проверки прав на комментарий
def check_comment_permission(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    comment = crud.get_comment(db, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if comment.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return comment