from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from datetime import datetime


class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOAuthCreate(BaseModel):
    name: str
    email: EmailStr
    github_id: str

class UserRead(UserBase):
    id: int
    registered_at: datetime
    is_author: bool
    is_admin: bool
    avatar: Optional[str] = None
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str


class NewsBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: Any
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
    text: str = Field(..., min_length=1)

class CommentCreate(CommentBase):
    news_id: int

class CommentRead(CommentBase):
    id: int
    news_id: int
    author_id: int
    published_at: datetime
    class Config:
        from_attributes = True


class SessionRead(BaseModel):
    id: int
    user_agent: Optional[str]
    created_at: datetime
    expires_at: datetime
    class Config:
        from_attributes = True