from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr
    avatar: Optional[str] = None

class UserCreate(UserBase):
    is_author: Optional[bool] = False

class UserRead(UserBase):
    id: int
    registered_at: datetime
    is_author: bool
    class Config:
        from_attributes = True

class NewsBase(BaseModel):
    title: str
    content: Any  # JSON-compatible
    cover: Optional[str] = None

class NewsCreate(NewsBase):
    pass

class NewsRead(NewsBase):
    id: int
    published_at: datetime
    author_id: int
    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    text: str

class CommentCreate(CommentBase):
    news_id: int
    author_id: int

class CommentRead(CommentBase):
    id: int
    news_id: int
    author_id: int
    published_at: datetime
    class Config:
        from_attributes = True
