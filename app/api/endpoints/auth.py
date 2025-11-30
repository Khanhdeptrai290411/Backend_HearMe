from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Any

from app.core.deps import get_db,get_current_active_user  
from app.services.auth import (
    authenticate_user,
    create_access_token,
    create_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.schemas.user import UserCreate, UserResponse, Token
from app.models.user import UserUpdate

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)) -> Any:
    """
    Register a new user.
    """
    return create_user(db, user)

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
        "sub": user.email,
        "role": user.role,
        "fullName": user.fullName  # <--- Thêm dòng này
    },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get an access token for future requests.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "fullName": user.fullName},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    } 
@router.get("/me", response_model=UserResponse)
async def get_current_user_details(current_user: dict = Depends(get_current_active_user)):
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's information.
    """
    from app.services.auth import get_password_hash
    from sqlalchemy import text
    
    user_id = current_user["id"]
    update_fields = []
    params = {"user_id": user_id}
    
    if user_update.fullName is not None:
        update_fields.append("fullName = :fullName")
        params["fullName"] = user_update.fullName
    if user_update.email is not None:
        # Check if email already exists (excluding current user)
        check_result = db.execute(
            text("SELECT id FROM users WHERE email = :email AND id != :user_id"),
            {"email": user_update.email, "user_id": user_id}
        )
        if check_result.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        update_fields.append("email = :email")
        params["email"] = user_update.email
    if user_update.password is not None:
        hashed_password = get_password_hash(user_update.password)
        update_fields.append("password = :password")
        params["password"] = hashed_password
    
    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    # Build update query
    update_query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = :user_id"
    result = db.execute(text(update_query), params)
    db.commit()
    
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get updated user
    updated_result = db.execute(
        text("SELECT id, email, fullName, role FROM users WHERE id = :user_id"),
        {"user_id": user_id}
    )
    updated_user = updated_result.fetchone()
    
    return {
        "id": updated_user.id,
        "email": updated_user.email,
        "fullName": updated_user.fullName,
        "role": updated_user.role
    }