from pydantic import BaseModel
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

    class Config:
        from_attributes = True 