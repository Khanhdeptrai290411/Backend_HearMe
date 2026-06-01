from typing import List  # Đảm bảo có List cho trường frames
from pydantic import BaseModel, ConfigDict # Đảm bảo có cả hai cái này
class VideoProcessRequest(BaseModel):
    frames: List[str]
    lessonPath: str
    modelId: int
    userId: int  # 👈 Thêm userId để lưu tiến trình
    model_config = ConfigDict(protected_namespaces=()) # THÊM DÒNG NÀY