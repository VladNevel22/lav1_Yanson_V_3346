from fastapi import Depends, Header, HTTPException
from .db import SessionLocal
from sqlalchemy.orm import Session
from . import crud

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Простая "авторизация" через X-User-Id — для демо
def get_current_user(x_user_id: int = Header(...), db: Session = Depends(get_db)):
    user = crud.get_user(db, x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# В продакшне замени на JWT/OAuth2.
