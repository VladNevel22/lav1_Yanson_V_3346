from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, crud
from ..deps import get_db, get_current_admin_user, get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=schemas.UserRead)
def get_me(current_user = Depends(get_current_user)):
    return current_user

@router.post("/", response_model=schemas.UserRead)
def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(400, "Email already exists")
    return crud.create_user(db, user_in)

@router.get("/{user_id}", response_model=schemas.UserRead)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    u = crud.get_user(db, user_id)
    if not u:
        raise HTTPException(404, "Not found")
    return u

@router.get("/", response_model=list[schemas.UserRead])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    return crud.list_users(db, skip, limit)

@router.patch("/{user_id}", response_model=schemas.UserRead)
def update_user(
    user_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    user = crud.update_user(db, user_id, data)
    if not user:
        raise HTTPException(404, "User not found")
    return user