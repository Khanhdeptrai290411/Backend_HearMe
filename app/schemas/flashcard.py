from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

# Định nghĩa cấu hình chung để dùng lại cho tất cả các class
# giúp code gọn gàng và tránh lỗi conflict
shared_config = ConfigDict(
    protected_namespaces=(),
    from_attributes=True,
    populate_by_name=True
)

class QuizBase(BaseModel):
    definition: str
    mota: str
    image: Optional[str] = None
    model_config = shared_config

class QuizCreate(QuizBase):
    pass

class Quiz(QuizBase):
    quizzes_id: int
    user_id: int
    course_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    # Đã kế thừa model_config từ QuizBase, không cần khai báo lại
    # ĐÃ XÓA class Config cũ ở đây

class CourseBase(BaseModel):
    title: str
    description: str
    nameschool: Optional[str] = None
    namecourse: Optional[str] = None
    model_config = shared_config

class CourseCreate(CourseBase):
    pass

class Course(CourseBase):
    course_id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    quizzes: List[Quiz] = []
    # Đã kế thừa model_config từ CourseBase, không cần khai báo lại
    # ĐÃ XÓA class Config cũ ở đây