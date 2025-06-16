from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..models.course import Model, ModelCreate, Chapter, ChapterCreate, Video, VideoCreate, ModelWithChapters
from ..config.database import get_db_connection

router = APIRouter()

# Model endpoints
@router.get("/models/", response_model=List[ModelWithChapters])
async def get_models():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        # Get all models
        cursor.execute("SELECT * FROM models")
        models = cursor.fetchall()

        # For each model, get its chapters and videos
        for model in models:
            cursor.execute("SELECT * FROM chapters WHERE model_id = %s", (model['id'],))
            chapters = cursor.fetchall()
            
            # For each chapter, get its videos
            for chapter in chapters:
                cursor.execute("SELECT * FROM videos WHERE chapter_id = %s", (chapter['id'],))
                chapter['videos'] = cursor.fetchall()
            
            model['chapters'] = chapters

        return models
    finally:
        cursor.close()
        conn.close()

@router.get("/models/{model_id}", response_model=ModelWithChapters)
async def get_model(model_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        # Get model
        cursor.execute("SELECT * FROM models WHERE id = %s", (model_id,))
        model = cursor.fetchone()
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")

        # Get chapters
        cursor.execute("SELECT * FROM chapters WHERE model_id = %s", (model_id,))
        chapters = cursor.fetchall()

        # Get videos for each chapter
        for chapter in chapters:
            cursor.execute("SELECT * FROM videos WHERE chapter_id = %s", (chapter['id'],))
            chapter['videos'] = cursor.fetchall()

        model['chapters'] = chapters
        return model
    finally:
        cursor.close()
        conn.close()

@router.post("/models/", response_model=Model)
async def create_model(model: ModelCreate):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "INSERT INTO models (name, threshold, target_shape, embedding_dir, model_file) VALUES (%s, %s, %s, %s, %s)",
            (model.name, model.threshold, model.target_shape, model.embedding_dir, model.model_file)
        )
        conn.commit()
        model_id = cursor.lastrowid
        cursor.execute("SELECT * FROM models WHERE id = %s", (model_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

# Chapter endpoints
@router.get("/chapters/", response_model=List[Chapter])
async def get_chapters():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM chapters")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

@router.get("/chapters/{chapter_id}", response_model=Chapter)
async def get_chapter(chapter_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM chapters WHERE id = %s", (chapter_id,))
        chapter = cursor.fetchone()
        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")
        return chapter
    finally:
        cursor.close()
        conn.close()

@router.post("/chapters/", response_model=Chapter)
async def create_chapter(chapter: ChapterCreate):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "INSERT INTO chapters (model_id, name, description) VALUES (%s, %s, %s)",
            (chapter.model_id, chapter.name, chapter.description)
        )
        conn.commit()
        chapter_id = cursor.lastrowid
        cursor.execute("SELECT * FROM chapters WHERE id = %s", (chapter_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

# Video endpoints
@router.get("/videos/", response_model=List[Video])
async def get_videos():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM videos")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

@router.get("/videos/{video_id}", response_model=Video)
async def get_video(video_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM videos WHERE id = %s", (video_id,))
        video = cursor.fetchone()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        return video
    finally:
        cursor.close()
        conn.close()

@router.post("/videos/", response_model=Video)
async def create_video(video: VideoCreate):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "INSERT INTO videos (model_id, chapter_id, video_filename) VALUES (%s, %s, %s)",
            (video.model_id, video.chapter_id, video.video_filename)
        )
        conn.commit()
        video_id = cursor.lastrowid
        cursor.execute("SELECT * FROM videos WHERE id = %s", (video_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

# Update endpoints
@router.put("/models/{model_id}", response_model=Model)
async def update_model(model_id: int, model: ModelCreate):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "UPDATE models SET name = %s, threshold = %s, target_shape = %s, embedding_dir = %s, model_file = %s WHERE id = %s",
            (model.name, model.threshold, model.target_shape, model.embedding_dir, model.model_file, model_id)
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Model not found")
        cursor.execute("SELECT * FROM models WHERE id = %s", (model_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

@router.put("/chapters/{chapter_id}", response_model=Chapter)
async def update_chapter(chapter_id: int, chapter: ChapterCreate):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "UPDATE chapters SET model_id = %s, name = %s, description = %s WHERE id = %s",
            (chapter.model_id, chapter.name, chapter.description, chapter_id)
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Chapter not found")
        cursor.execute("SELECT * FROM chapters WHERE id = %s", (chapter_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

@router.put("/videos/{video_id}", response_model=Video)
async def update_video(video_id: int, video: VideoCreate):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "UPDATE videos SET model_id = %s, chapter_id = %s, video_filename = %s WHERE id = %s",
            (video.model_id, video.chapter_id, video.video_filename, video_id)
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Video not found")
        cursor.execute("SELECT * FROM videos WHERE id = %s", (video_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

# Delete endpoints
@router.delete("/models/{model_id}")
async def delete_model(model_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM models WHERE id = %s", (model_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Model not found")
        return {"message": "Model deleted successfully"}
    finally:
        cursor.close()
        conn.close()

@router.delete("/chapters/{chapter_id}")
async def delete_chapter(chapter_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chapters WHERE id = %s", (chapter_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Chapter not found")
        return {"message": "Chapter deleted successfully"}
    finally:
        cursor.close()
        conn.close()

@router.delete("/videos/{video_id}")
async def delete_video(video_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM videos WHERE id = %s", (video_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Video not found")
        return {"message": "Video deleted successfully"}
    finally:
        cursor.close()
        conn.close()

# Get chapters by model ID
@router.get("/models/{model_id}/chapters", response_model=List[Chapter])
async def get_chapters_by_model(model_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM chapters WHERE model_id = %s", (model_id,))
        chapters = cursor.fetchall()
        return chapters
    finally:
        cursor.close()
        conn.close()

# Get videos by chapter ID
@router.get("/chapters/{chapter_id}/videos", response_model=List[Video])
async def get_videos_by_chapter(chapter_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM videos WHERE chapter_id = %s", (chapter_id,))
        videos = cursor.fetchall()
        return videos
    finally:
        cursor.close()
        conn.close()

@router.get("/user-progress/{user_id}", response_model=List[int])
async def get_user_progress(user_id: int):
    """Lấy danh sách video_id mà user đã hoàn thành"""
    print(f"\n=== Getting progress for user {user_id} ===")
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT DISTINCT video_id 
            FROM user_video_progress 
            WHERE user_id = %s AND is_completed = TRUE
            ORDER BY video_id
        """
        print(f"Executing query: {query}")
        print(f"With parameters: {(user_id,)}")
        
        cursor.execute(query, (user_id,))
        results = cursor.fetchall()
        
        print(f"Raw query results: {results}")
        
        if not results:
            print("No completed videos found")
            return []
            
        video_ids = [row['video_id'] for row in results]
        print(f"Found {len(video_ids)} completed videos for user {user_id}: {video_ids}")
        
        # Verify data in database
        verify_query = "SELECT * FROM user_video_progress WHERE user_id = %s"
        cursor.execute(verify_query, (user_id,))
        all_progress = cursor.fetchall()
        print(f"All progress records for user: {all_progress}")
        
        return video_ids
    except Exception as e:
        print(f"Error fetching user progress: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return []
    finally:
        cursor.close()
        conn.close() 