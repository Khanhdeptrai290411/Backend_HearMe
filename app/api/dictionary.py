from fastapi import APIRouter, HTTPException, Depends, Query,Request
from typing import List, Optional
from pydantic import BaseModel
from ..config.database import get_db_connection
from sqlalchemy.orm import Session
# from ..config.database import get_db_connection
from app.models.vocabulary import Vocabulary
from app.models.topic import Topic
from app.schemas.vocabulary import VocabularyResponse
import logging
from .dictionary_admin import router1
# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
router.include_router(router1, prefix="/admin", tags=["dictionary-admin"])
class Topic(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

class VocabularySchema(BaseModel):
    id: int
    word: str
    meaning: str
    video_url: Optional[str] = None
    image_url: Optional[str] = None
    topic_id: Optional[int] = None
    topic_name: Optional[str] = None

    class Config:
        from_attributes = True

class VocabularyResponse(BaseModel):
    status: str
    data: List[VocabularySchema]

@router.get("/topics/", response_model=List[Topic])
async def get_topics(db: Session = Depends(get_db_connection)):
    topics = db.query(Topic).all()
    return topics

@router.get("/vocabularies", response_model=dict)
def get_vocabularies(
    word: Optional[str] = None,
    limit: int = 1000,
    offset: int = 0
):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Could not connect to database")
            
        cursor = conn.cursor(dictionary=True)
        
        # Base query with JOIN to get topic name
        sql = """
            SELECT 
                v.id,
                v.word,
                v.meaning,
                v.video_url,
                v.image_url,
                v.topic_id,
                t.name as topic_name
            FROM vocabularies v 
            LEFT JOIN topics t ON v.topic_id = t.id 
            WHERE 1=1
        """
        params = []
        
        if word:
            sql += " AND LOWER(v.word) LIKE LOWER(%s)"
            params.append(f"%{word}%")
            
        # Add pagination
        sql += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        # Log the query for debugging
        logger.info(f"Executing query: {sql}")
        logger.info(f"With params: {params}")
        
        cursor.execute(sql, tuple(params))
        results = cursor.fetchall()
        
        # Map results to schema
        vocabularies = []
        for result in results:
            vocab = {
                "id": result.get("id"),
                "word": result.get("word"),
                "meaning": result.get("meaning"),
                "video_url": result.get("video_url"),
                "image_url": result.get("image_url"),
                "topic_id": result.get("topic_id"),
                "topic_name": result.get("topic_name")
            }
            vocabularies.append(vocab)
        
        # Get total count
        count_sql = """
            SELECT COUNT(*) as total 
            FROM vocabularies v 
            LEFT JOIN topics t ON v.topic_id = t.id 
            WHERE 1=1
        """
        if word:
            count_sql += " AND LOWER(v.word) LIKE LOWER(%s)"
            
        cursor.execute(count_sql, tuple(params[:-2]))
        total = cursor.fetchone()["total"]
        
        # Log the results
        logger.info(f"Found {len(vocabularies)} vocabularies")
        logger.info(f"Total count: {total}")
        
        return {
            "data": vocabularies,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error fetching vocabularies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching vocabularies: {str(e)}")
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception as e:
                logger.error(f"Error closing cursor: {str(e)}")
        if conn:
            try:
                conn.close()
            except Exception as e:
                logger.error(f"Error closing connection: {str(e)}")

@router.get("/words/{word}", response_model=VocabularySchema)
async def get_vocabulary(word: str):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Could not connect to database")
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                v.id,
                v.word,
                v.meaning,
                v.video_url,
                v.image_url,
                v.topic_id,
                t.name as topic_name
            FROM vocabularies v 
            LEFT JOIN topics t ON v.topic_id = t.id 
            WHERE LOWER(v.word) = LOWER(%s)
        """, (word,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail=f"Vocabulary with word '{word}' not found")
            
        # Map database result to schema
        vocab = {
            "id": result["id"],
            "word": result["word"],
            "meaning": result["meaning"],
            "video_url": result["video_url"],
            "image_url": result["image_url"],
            "topic_id": result["topic_id"],
            "topic_name": result["topic_name"]
        }
        
        return vocab
    except Exception as e:
        logger.error(f"Error fetching vocabulary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching vocabulary: {str(e)}")
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception as e:
                logger.error(f"Error closing cursor: {str(e)}")
        if conn:
            try:
                conn.close()
            except Exception as e:
                logger.error(f"Error closing connection: {str(e)}") 
@router.post("/search", response_model=dict)
async def search_vocabularies(request: Request):
    conn = None
    cursor = None
    try:
        # Parse request body
        body = await request.json()
        search_term = body.get("search_term", "")
        limit = body.get("limit", 1000)
        offset = body.get("offset", 0)

        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Could not connect to database")
            
        cursor = conn.cursor(dictionary=True)
        
        # Base query with JOIN to get topic name
        sql = """
            SELECT 
                v.id,
                v.word,
                v.meaning,
                v.video_url,
                v.image_url,
                v.topic_id,
                t.name as topic_name
            FROM vocabularies v 
            LEFT JOIN topics t ON v.topic_id = t.id 
            WHERE 1=1
        """
        params = []
        
        if search_term:
            # Search only in word field
            sql += " AND LOWER(v.word) LIKE LOWER(%s)"
            params.append(f"%{search_term}%")
            
        # Add pagination
        sql += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        # Log the query for debugging
        logger.info(f"Executing search query: {sql}")
        logger.info(f"With params: {params}")
        
        cursor.execute(sql, tuple(params))
        results = cursor.fetchall()
        
        # Map results to schema
        vocabularies = []
        for result in results:
            vocab = {
                "id": result.get("id"),
                "word": result.get("word"),
                "meaning": result.get("meaning"),
                "video_url": result.get("video_url"),
                "image_url": result.get("image_url"),
                "topic_id": result.get("topic_id"),
                "topic_name": result.get("topic_name")
            }
            vocabularies.append(vocab)
        
        # Get total count with the same word-only condition
        count_sql = """
            SELECT COUNT(*) as total 
            FROM vocabularies v 
            LEFT JOIN topics t ON v.topic_id = t.id 
            WHERE 1=1
        """
        count_params = []
        
        if search_term:
            count_sql += " AND LOWER(v.word) LIKE LOWER(%s)"
            count_params.append(f"%{search_term}%")
            
        cursor.execute(count_sql, tuple(count_params))
        total = cursor.fetchone()["total"]
        
        # Log the results
        logger.info(f"Found {len(vocabularies)} matching vocabularies")
        logger.info(f"Total count: {total}")
        
        return {
            "data": vocabularies,
            "total": total,
            "limit": limit,
            "offset": offset,
            "search_term": search_term
        }
    except Exception as e:
        logger.error(f"Error searching vocabularies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching vocabularies: {str(e)}")
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception as e:
                logger.error(f"Error closing cursor: {str(e)}")
        if conn:
            try:
                conn.close()
            except Exception as e:
                logger.error(f"Error closing connection: {str(e)}") 