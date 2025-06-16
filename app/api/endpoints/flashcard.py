from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.deps import get_db, get_current_user
from app.services.flashcard import FlashcardService
from app.schemas.flashcard import Course, CourseCreate, Quiz, QuizCreate
import os
import shutil

router = APIRouter()

@router.post("/courses/", response_model=Course)
async def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new course.
    """
    return await FlashcardService.create_course(db, course, current_user["id"])

@router.get("/courses/", response_model=List[Course])
async def get_courses(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all courses.
    """
    return await FlashcardService.get_user_courses(db, current_user["id"])

@router.get("/courses/{course_id}", response_model=Course)
async def get_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific course by ID.
    """
    try:
        course = await FlashcardService.get_course(db, course_id)
        if not course or course["user_id"] != current_user["id"]:
            raise HTTPException(status_code=404, detail="Course not found")
        return course
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_course endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching course: {str(e)}"
        )

@router.put("/courses/{course_id}", response_model=Course)
async def update_course(
    course_id: int,
    course: CourseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update a course.
    """
    return await FlashcardService.update_course(db, course_id, course, current_user["id"])

@router.delete("/courses/{course_id}")
async def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a course.
    """
    return FlashcardService.delete_course(db, course_id, current_user["id"])

@router.post("/courses/{course_id}/upload-image")
async def upload_course_image(
    course_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload an image for a course.
    """
    course = await FlashcardService.get_course(db, course_id)
    if not course or course.user_id != current_user["id"]:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return await FlashcardService.upload_course_image(db, course_id, file)

@router.post("/courses/{course_id}/quizzes/", response_model=Quiz)
async def create_quiz(
    course_id: int,
    definition: str = Form(...),
    mota: str = Form(...),
    media_file: Optional[UploadFile] = File(None),
    media_type: Optional[str] = Form(None),  # 'image' or 'video'
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new quiz for a course"""
    course = await FlashcardService.get_course(db, course_id)
    if not course or course["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Course not found")
    
    quiz_data = QuizCreate(definition=definition, mota=mota)
    return await FlashcardService.create_quiz(
        db, 
        quiz_data, 
        course_id, 
        current_user["id"], 
        media_file=media_file,
        media_type=media_type
    )

@router.get("/courses/{course_id}/quizzes/", response_model=List[Quiz])
async def get_course_quizzes(
    course_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all quizzes for a course"""
    course = await FlashcardService.get_course(db, course_id)
    if not course or course.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Course not found")
    return await FlashcardService.get_course_quizzes(db, course_id)

@router.delete("/quizzes/{quiz_id}")
async def delete_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a quiz"""
    try:
        result = await FlashcardService.delete_quiz(db, quiz_id, current_user["id"])
        if result:
            return {"message": "Quiz deleted successfully"}
        return {"message": "Quiz not found or already deleted"}
    except Exception as e:
        print(f"Error deleting quiz: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting quiz: {str(e)}"
        )

@router.put("/quizzes/{quiz_id}", response_model=Quiz)
async def update_quiz(
    quiz_id: int,
    definition: str = Form(...),
    mota: str = Form(...),
    media_file: Optional[UploadFile] = File(None),
    media_type: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update an existing quiz"""
    try:
        # Create quiz data
        quiz_data = QuizCreate(definition=definition, mota=mota)
        
        # Update the quiz
        return await FlashcardService.update_quiz(
            db=db,
            quiz_id=quiz_id,
            quiz_data=quiz_data,
            user_id=current_user["id"],
            media_file=media_file,
            media_type=media_type
        )
    except Exception as e:
        print(f"Error updating quiz: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating quiz: {str(e)}"
        ) 