from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from ..config.database import get_db_connection

router1 = APIRouter()

class Topic(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

class Vocabulary(BaseModel):
    id: int
    word: str
    meaning: str
    video_url: Optional[str] = None
    image_url: Optional[str] = None
    topic_id: Optional[int] = None
    topic_name: Optional[str] = None

@router1.get("/topics/", response_model=List[Topic])
async def get_topics():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM topics")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

@router1.get("/vocabularies/", response_model=List[Vocabulary])
async def get_vocabularies(search: Optional[str] = None, topic_id: Optional[int] = None):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        
        base_query = """
            SELECT v.*, t.name as topic_name 
            FROM vocabularies v 
            LEFT JOIN topics t ON v.topic_id = t.id
            WHERE 1=1
        """
        params = []

        if search:
            base_query += " AND (v.word LIKE %s OR v.meaning LIKE %s)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param])

        if topic_id:
            base_query += " AND v.topic_id = %s"
            params.append(topic_id)

        cursor.execute(base_query, params)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

@router1.get("/vocabularies/{vocab_id}", response_model=Vocabulary)
async def get_vocabulary(vocab_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT v.*, t.name as topic_name 
            FROM vocabularies v 
            LEFT JOIN topics t ON v.topic_id = t.id 
            WHERE v.id = %s
        """, (vocab_id,))
        vocab = cursor.fetchone()
        if not vocab:
            raise HTTPException(status_code=404, detail="Vocabulary not found")
        return vocab
    finally:
        cursor.close()
        conn.close() 