class VideoProcessRequest(BaseModel):
    frames: List[str]
    lessonPath: str
    modelId: int
    userId: int  # 👈 Thêm userId để lưu tiến trình
