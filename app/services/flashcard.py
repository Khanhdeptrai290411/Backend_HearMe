from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import UploadFile, HTTPException
import os
from datetime import datetime
from sqlalchemy.sql import text
from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.flashcard import Course, Quiz
from app.schemas.flashcard import CourseCreate, QuizCreate

class FlashcardService:
    @staticmethod
    async def create_course(db: Session, course: CourseCreate, user_id: int) -> Course:
        try:
            print(f"Creating course with data: {course.dict()}, user_id: {user_id}")
            
            # Create new course
            db_course = Course(
                user_id=user_id,
                title=course.title,
                description=course.description,
                nameschool=course.nameschool,
                namecourse=course.namecourse
            )
            
            print(f"Course object created: {db_course.__dict__}")
            
            db.add(db_course)
            db.commit()
            db.refresh(db_course)
            
            print(f"Course saved successfully: {db_course.__dict__}")
            
            # Convert to dictionary for response
            return {
                "course_id": db_course.course_id,
                "user_id": db_course.user_id,
                "title": db_course.title,
                "description": db_course.description,
                "nameschool": db_course.nameschool,
                "namecourse": db_course.namecourse,
                "created_at": db_course.created_at,
                "updated_at": db_course.updated_at,
                "quizzes": []
            }
        except Exception as e:
            print(f"Error creating course: {str(e)}")
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error creating course: {str(e)}"
            )

    @staticmethod
    async def get_user_courses(db: Session, user_id: int, skip: int = 0, limit: int = 10) -> List[Course]:
        try:
            # Use text() for raw SQL to ensure proper parameter binding
            result = db.execute(
                text("""
                    SELECT c.*, u.email as user_email, u.fullName as user_fullName
                    FROM courses c
                    JOIN users u ON c.user_id = u.id
                    WHERE c.user_id = :user_id
                    ORDER BY c.created_at DESC
                    LIMIT :limit OFFSET :skip
                """),
                {
                    "user_id": user_id,
                    "limit": limit,
                    "skip": skip
                }
            )
            
            # Convert result to list of dictionaries
            courses = []
            for row in result:
                course_dict = {
                    "course_id": row.course_id,
                    "user_id": row.user_id,
                    "title": row.title,
                    "description": row.description,
                    "nameschool": row.nameschool,
                    "namecourse": row.namecourse,
                    "created_at": row.created_at,
                    "updated_at": row.updated_at
                }
                courses.append(course_dict)
            
            return courses
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching courses: {str(e)}"
            )

    @staticmethod
    async def get_course(db: Session, course_id: int) -> Optional[Course]:
        try:
            print(f"Fetching course with id: {course_id}")
            
            # Use text() for raw SQL to ensure proper parameter binding
            result = db.execute(
                text("""
                    SELECT c.*, u.email as user_email, u.fullName as user_fullName
                    FROM courses c
                    JOIN users u ON c.user_id = u.id
                    WHERE c.course_id = :course_id
                """),
                {"course_id": course_id}
            )
            
            course = result.fetchone()
            if not course:
                raise HTTPException(status_code=404, detail="Course not found")

            # Convert row to dictionary using proper SQLAlchemy method
            course_dict = dict(course._mapping)
            print(f"Course found: {course_dict}")
            
            # Get quizzes for this course
            quizzes_result = db.execute(
                text("""
                    SELECT * FROM quizzes
                    WHERE course_id = :course_id
                    ORDER BY created_at DESC
                """),
                {"course_id": course_id}
            )
            
            quizzes = []
            for quiz_row in quizzes_result:
                # Convert row to dictionary using proper SQLAlchemy method
                quiz_dict = dict(quiz_row._mapping)
                quizzes.append({
                    "quizzes_id": quiz_dict["quizzes_id"],
                    "user_id": quiz_dict["user_id"],
                    "course_id": quiz_dict["course_id"],
                    "definition": quiz_dict["definition"],
                    "mota": quiz_dict["mota"],
                    "image": quiz_dict["image"],
                    "created_at": quiz_dict["created_at"],
                    "updated_at": quiz_dict["updated_at"]
                })

            # Return the course data in the expected format
            return {
                "course_id": course_dict["course_id"],
                "user_id": course_dict["user_id"],
                "title": course_dict["title"],
                "description": course_dict["description"],
                "nameschool": course_dict["nameschool"],
                "namecourse": course_dict["namecourse"],
                "created_at": course_dict["created_at"],
                "updated_at": course_dict["updated_at"],
                "quizzes": quizzes
            }
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error fetching course: {str(e)}")
            print(f"Exception type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching course: {str(e)}"
            )

    @staticmethod
    async def create_quiz(
        db: Session, 
        quiz: QuizCreate, 
        course_id: int, 
        user_id: int,
        media_file: Optional[UploadFile] = None,
        media_type: Optional[str] = None
    ) -> Quiz:
        try:
            file_path = None
            if media_file and media_type:
                # Create uploads directory if it doesn't exist
                os.makedirs("public/uploads", exist_ok=True)
                
                # Save file with unique name
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_extension = os.path.splitext(media_file.filename)[1]
                file_name = f"{timestamp}{file_extension}"
                
                # Save file and store relative path
                save_path = os.path.join("public/uploads", file_name)
                file_path = f"uploads/{file_name}"  # Store relative path for database
                
                print(f"Saving file to: {save_path}")
                print(f"Database path: {file_path}")
                
                with open(save_path, "wb") as buffer:
                    content = await media_file.read()
                    buffer.write(content)
                    print(f"File saved successfully, size: {len(content)} bytes")

            db_quiz = Quiz(
                course_id=course_id,
                user_id=user_id,
                definition=quiz.definition,
                mota=quiz.mota,
                image=file_path  # Store both image and video paths in the image field
            )
            db.add(db_quiz)
            db.commit()
            db.refresh(db_quiz)

            result = {
                "quizzes_id": db_quiz.quizzes_id,
                "user_id": db_quiz.user_id,
                "course_id": db_quiz.course_id,
                "definition": db_quiz.definition,
                "mota": db_quiz.mota,
                "image": db_quiz.image,
                "created_at": db_quiz.created_at,
                "updated_at": db_quiz.updated_at
            }
            print(f"Created quiz with data: {result}")
            return result

        except Exception as e:
            print(f"Error creating quiz: {str(e)}")
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error creating quiz: {str(e)}"
            )

    @staticmethod
    async def get_course_quizzes(db: Session, course_id: int) -> List[Quiz]:
        return db.query(Quiz).filter(Quiz.course_id == course_id).all()

    @staticmethod
    async def delete_quiz(db: Session, quiz_id: int, user_id: int) -> bool:
        try:
            # Get the quiz first to check ownership and get file path
            quiz = db.query(Quiz).filter(Quiz.quizzes_id == quiz_id, Quiz.user_id == user_id).first()
            if not quiz:
                return False

            # Delete associated media file if exists
            if quiz.image and os.path.exists(f"public/{quiz.image}"):
                try:
                    os.remove(f"public/{quiz.image}")
                except Exception as e:
                    print(f"Warning: Could not delete file {quiz.image}: {str(e)}")

            # Delete the quiz from database
            db.delete(quiz)
            db.commit()
            return True
            
        except Exception as e:
            print(f"Error in delete_quiz: {str(e)}")
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting quiz: {str(e)}"
            )

    @staticmethod
    async def update_quiz(
        db: Session, 
        quiz_id: int, 
        quiz_data: QuizCreate, 
        user_id: int,
        media_file: Optional[UploadFile] = None,
        media_type: Optional[str] = None
    ) -> Quiz:
        try:
            # Get existing quiz
            quiz = db.query(Quiz).filter(Quiz.quizzes_id == quiz_id, Quiz.user_id == user_id).first()
            if not quiz:
                raise HTTPException(status_code=404, detail="Quiz not found")

            # Handle media file if provided
            if media_file and media_type:
                # Delete old file if exists
                if quiz.image and os.path.exists(f"public/{quiz.image}"):
                    os.remove(f"public/{quiz.image}")
                
                # Save new file
                os.makedirs("public/uploads", exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_extension = os.path.splitext(media_file.filename)[1]
                file_name = f"{timestamp}{file_extension}"
                file_path = f"uploads/{file_name}"
                
                with open(f"public/{file_path}", "wb") as buffer:
                    buffer.write(await media_file.read())
                
                quiz.image = file_path

            # Update other fields
            quiz.definition = quiz_data.definition
            quiz.mota = quiz_data.mota
            quiz.updated_at = datetime.now()

            db.commit()
            db.refresh(quiz)

            return {
                "quizzes_id": quiz.quizzes_id,
                "user_id": quiz.user_id,
                "course_id": quiz.course_id,
                "definition": quiz.definition,
                "mota": quiz.mota,
                "image": quiz.image,
                "created_at": quiz.created_at,
                "updated_at": quiz.updated_at
            }
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error updating quiz: {str(e)}")
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error updating quiz: {str(e)}"
            )

    @staticmethod
    async def update_course(db: Session, course_id: int, course: CourseCreate, user_id: int) -> Course:
        try:
            # First update the course
            result = db.execute(
                text("""
                    UPDATE courses
                    SET title = :title,
                        description = :description,
                        nameschool = :nameschool,
                        namecourse = :namecourse,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE course_id = :course_id AND user_id = :user_id
                """),
                {
                    "course_id": course_id,
                    "user_id": user_id,
                    "title": course.title,
                    "description": course.description,
                    "nameschool": course.nameschool,
                    "namecourse": course.namecourse
                }
            )
            db.commit()
            
            # Then fetch the updated course
            updated_result = db.execute(
                text("""
                    SELECT c.*, u.email as user_email, u.fullName as user_fullName
                    FROM courses c
                    JOIN users u ON c.user_id = u.id
                    WHERE c.course_id = :course_id AND c.user_id = :user_id
                """),
                {
                    "course_id": course_id,
                    "user_id": user_id
                }
            )
            
            updated_course = updated_result.fetchone()
            if not updated_course:
                raise HTTPException(status_code=404, detail="Course not found or you don't have permission to update it")

            # Convert row to dictionary using proper SQLAlchemy method
            course_dict = dict(updated_course._mapping)
            
            # Get quizzes for this course
            quizzes_result = db.execute(
                text("""
                    SELECT * FROM quizzes
                    WHERE course_id = :course_id
                    ORDER BY created_at DESC
                """),
                {"course_id": course_id}
            )
            
            quizzes = []
            for quiz_row in quizzes_result:
                quiz_dict = dict(quiz_row._mapping)
                quizzes.append({
                    "quizzes_id": quiz_dict["quizzes_id"],
                    "user_id": quiz_dict["user_id"],
                    "course_id": quiz_dict["course_id"],
                    "definition": quiz_dict["definition"],
                    "mota": quiz_dict["mota"],
                    "image": quiz_dict["image"],
                    "created_at": quiz_dict["created_at"],
                    "updated_at": quiz_dict["updated_at"]
                })

            return {
                "course_id": course_dict["course_id"],
                "user_id": course_dict["user_id"],
                "title": course_dict["title"],
                "description": course_dict["description"],
                "nameschool": course_dict["nameschool"],
                "namecourse": course_dict["namecourse"],
                "created_at": course_dict["created_at"],
                "updated_at": course_dict["updated_at"],
                "quizzes": quizzes
            }
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error updating course: {str(e)}")
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error updating course: {str(e)}"
            )

    @staticmethod
    def delete_course(db: Session, course_id: int, user_id: int):
        try:
            # Get the course
            course = db.query(Course).filter(
                Course.course_id == course_id,
                Course.user_id == user_id
            ).first()

            if not course:
                raise HTTPException(
                    status_code=404,
                    detail="Course not found or you don't have permission to delete it"
                )

            # Delete all quizzes associated with the course
            db.query(Quiz).filter(Quiz.course_id == course_id).delete()

            # Delete the course
            db.delete(course)
            db.commit()
            
            return {"message": "Course deleted successfully"}

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e)) 