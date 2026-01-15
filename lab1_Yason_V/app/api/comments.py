from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, crud
from ..deps import get_db, get_current_user, check_comment_permission

router = APIRouter(prefix="/comments", tags=["comments"])

@router.post("/", response_model=schemas.CommentRead)
def create_comment(
    comment_in: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    news = crud.get_news(db, comment_in.news_id)
    if not news:
        raise HTTPException(404, "News not found")
    
    return crud.create_comment(db, comment_in, author_id=current_user.id)

@router.patch("/{comment_id}", response_model=schemas.CommentRead)
def update_comment(
    comment_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    comment_obj = check_comment_permission(comment_id, db, current_user)
    return crud.update_comment(db, comment_obj, payload)

@router.delete("/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    comment_obj = check_comment_permission(comment_id, db, current_user)
    crud.delete_comment(db, comment_obj)
    return {"ok": True}