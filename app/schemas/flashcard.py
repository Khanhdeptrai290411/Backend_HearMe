from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class QuizBase(BaseModel):
    definition: str
    mota: str
    image: Optional[str] = None

class QuizCreate(QuizBase):
    pass

class Quiz(QuizBase):
    quizzes_id: int
    user_id: int
    course_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True

class CourseBase(BaseModel):
    title: str
    description: str
    nameschool: Optional[str] = None
    namecourse: Optional[str] = None

class CourseCreate(CourseBase):
    pass

class Course(CourseBase):
    course_id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    quizzes: List[Quiz] = []

    class Config:
        from_attributes = True
        populate_by_name = True 