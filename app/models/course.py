from pydantic import BaseModel
from typing import Optional, List, Union

class ModelBase(BaseModel):
    name: str
    threshold: Optional[float] = None
    target_shape: Optional[str] = None
    embedding_dir: Optional[str] = None
    model_file: Optional[str] = None

class ModelCreate(ModelBase):
    pass

class Model(ModelBase):
    id: int

    class Config:
        from_attributes = True

class ChapterBase(BaseModel):
    model_id: int
    name: str
    description: Optional[str] = None

class ChapterCreate(ChapterBase):
    pass

class Chapter(ChapterBase):
    id: int
    
    class Config:
        from_attributes = True

class VideoBase(BaseModel):
    model_id: int
    chapter_id: int
    video_filename: str

class VideoCreate(VideoBase):
    pass

class Video(VideoBase):
    id: int

    class Config:
        from_attributes = True

class ChapterWithVideos(Chapter):
    videos: List[Video] = []

class ModelWithChapters(Model):
    chapters: List[ChapterWithVideos] = [] 