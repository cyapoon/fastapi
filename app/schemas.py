from datetime import datetime
from typing import Optional, Annotated
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    
class UserOut(BaseModel):
    id:int
    email: EmailStr
    created_at: datetime
    
    class Config:
        from_attributes = True
        
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True
    
class PostCreate(PostBase):
    pass

class Post(BaseModel):
    id: int
    title: str
    content:str
    created_at: datetime
    published: bool
    owner_id: int
    owner: UserOut
    
    class Config:
        from_attributes = True
        
class PostOut(PostBase):
    Post: Post
    votes:int
    class Config:
        from_attributes = True
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    id: Optional[str] = None
    
class Vote(BaseModel):
    post_id: int
    dir: Annotated[int, Field(le=1)]