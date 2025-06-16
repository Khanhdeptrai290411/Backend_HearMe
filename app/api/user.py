from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..models.user import UserCreate, UserUpdate
from ..config.database import get_db_connection
from mysql.connector.pooling import PooledMySQLConnection
import bcrypt
from pydantic import BaseModel

class UserResponse(BaseModel):
    id: int
    fullName: str
    email: str
    role: str

    class Config:
        from_attributes = True

router = APIRouter()

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

@router.get("/users/", response_model=List[UserResponse])
def get_users():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, fullName, email, role FROM users")
        users = cursor.fetchall()
        return users
    finally:
        cursor.close()
        conn.close()

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, fullName, email, role FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    finally:
        cursor.close()
        conn.close()

@router.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        hashed_password = get_password_hash(user.password)
        cursor.execute(
            "INSERT INTO users (fullName, email, password, role) VALUES (%s, %s, %s, %s)",
            (user.fullName, user.email, hashed_password, user.role)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return {
            "id": user_id,
            "fullName": user.fullName,
            "email": user.email,
            "role": user.role
        }
    except Exception as e:
        conn.rollback()
        if "Duplicate entry" in str(e):
            raise HTTPException(status_code=400, detail="Email already registered")
        raise HTTPException(status_code=500, detail="Database error")
    finally:
        cursor.close()
        conn.close()

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        update_fields = []
        values = []
        
        if user.fullName is not None:
            update_fields.append("fullName = %s")
            values.append(user.fullName)
        if user.email is not None:
            update_fields.append("email = %s")
            values.append(user.email)
        if user.password is not None:
            update_fields.append("password = %s")
            values.append(get_password_hash(user.password))
        if user.role is not None:
            update_fields.append("role = %s")
            values.append(user.role)
            
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
            
        values.append(user_id)
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
        cursor.execute(query, values)
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
            
        cursor.execute("SELECT id, fullName, email, role FROM users WHERE id = %s", (user_id,))
        updated_user = cursor.fetchone()
        return updated_user
    finally:
        cursor.close()
        conn.close()

@router.delete("/users/{user_id}")
def delete_user(user_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deleted successfully"}
    finally:
        cursor.close()
        conn.close() 