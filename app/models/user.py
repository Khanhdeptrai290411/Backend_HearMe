from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    fullName: Optional[str] = None
    email: str
    role: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDB(UserBase):
    id: int
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True 