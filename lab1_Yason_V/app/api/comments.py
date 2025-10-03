from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, crud, models
from ..deps import get_db, get_current_user

router = APIRouter(prefix="/comments", tags=["comments"])

@router.post("/", response_model=schemas.CommentRead)
def create_comment(comment_in: schemas.CommentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Ensure author_id matches current_user (or allow admin)
    if comment_in.author_id != current_user.id:
        raise HTTPException(403, "Author id mismatch")
    # Ensure news exists
    news = crud.get_news(db, comment_in.news_id)
    if not news:
        raise HTTPException(404, "News not found")
    return crud.create_comment(db, comment_in)

@router.patch("/{comment_id}", response_model=schemas.CommentRead)
def update_comment(comment_id: int, payload: dict, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    c = crud.get_comment(db, comment_id)
    if not c:
        raise HTTPException(404, "Comment not found")
    if c.author_id != current_user.id:
        raise HTTPException(403, "Only author can update")
    return crud.update_comment(db, c, payload)

@router.delete("/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    c = crud.get_comment(db, comment_id)
    if not c:
        raise HTTPException(404, "Comment not found")
    if c.author_id != current_user.id:
        raise HTTPException(403, "Only author can delete")
    crud.delete_comment(db, c)
    return {"ok": True}
