from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

# Định nghĩa cấu hình chung một lần để tái sử dụng (tùy chọn)
shared_config = ConfigDict(
    protected_namespaces=(),
    from_attributes=True,
    populate_by_name=True
)

class UserBase(BaseModel):
    email: EmailStr
    fullName: str
    model_config = shared_config

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    model_config = shared_config

class UserResponse(UserBase):
    id: int
    role: str
    # model_config đã được kế thừa từ UserBase, 
    # nhưng nếu muốn chắc chắn bạn có thể ghi đè lại:
    model_config = shared_config

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    model_config = shared_config

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    model_config = ConfigDict(protected_namespaces=()) # THÊM DÒNG NÀY