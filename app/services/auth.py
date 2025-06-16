from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.schemas.user import UserCreate, TokenData
from fastapi import HTTPException, status

# JWT Configuration
SECRET_KEY = "your-secret-key-here"  # Change this in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_email(db: Session, email: str):
    result = db.execute(
        text("SELECT * FROM users WHERE email = :email"),
        {"email": email}
    )
    return result.fetchone()

def create_user(db: Session, user: UserCreate):
    try:
        # Check if user already exists
        db_user = get_user_by_email(db, user.email)
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user.password)
        
        print(f"Creating user with email: {user.email}, fullName: {user.fullName}")
        
        # First, insert the new user
        db.execute(
            text("""
                INSERT INTO users (email, fullName, password, role)
                VALUES (:email, :fullName, :password, 'user')
            """),
            {
                "email": user.email,
                "fullName": user.fullName,
                "password": hashed_password
            }
        )
        db.commit()
        
        # Then retrieve the newly created user
        result = db.execute(
            text("SELECT id, email, fullName, role FROM users WHERE email = :email"),
            {"email": user.email}
        )
        user_data = result.fetchone()
        
        if not user_data:
            print("Error: User was created but could not be retrieved")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User was created but could not be retrieved"
            )
        
        # Return data in UserResponse format
        return {
            "id": user_data.id,
            "email": user_data.email,
            "fullName": user_data.fullName,
            "role": user_data.role
        }
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        raise

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user 