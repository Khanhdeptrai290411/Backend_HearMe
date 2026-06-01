from pydantic import BaseModel, ConfigDict
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VocabularyResponse(BaseModel):
    id: int
    word: str
    meaning: str
    video_url: Optional[str] = None
    image_url: Optional[str] = None
    type: Optional[str] = None

    # Gộp tất cả cấu hình vào đây và XÓA class Config cũ đi
    model_config = ConfigDict(
        protected_namespaces=(),
        from_attributes=True
    )