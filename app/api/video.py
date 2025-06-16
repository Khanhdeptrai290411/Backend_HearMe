import os
import base64
import numpy as np
import cv2

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from app.models.schemas import VideoProcessRequest, VideoResponse
from app.services.landmark_service import LandmarkService
from app.services.model_service import ModelService
from app.services.roadmap_service import RoadmapService
from app.config.settings import FRAMES_LIMIT

router = APIRouter()
landmark_service = LandmarkService()
model_service = ModelService()
roadmap_service = RoadmapService(model_service)

@router.get("/roadmap")
async def get_roadmap():
    """Lấy danh sách các chương và bài học"""
    return roadmap_service.get_roadmap()

@router.post("/process-video", response_model=VideoResponse)
async def process_video(request: VideoProcessRequest):
    """
    Xử lý video từ người dùng và so sánh với video mẫu
    - frames: Danh sách các frame dạng base64
    - lessonPath: Đường dẫn đến bài học cần so sánh
    """
    frames = request.frames
    lesson_path = request.lessonPath

    roadmap = roadmap_service.get_roadmap()
    reference_embedding_path = None
    for chapter in roadmap.values():
        for lesson in chapter:
            if lesson["path"] == lesson_path:
                reference_embedding_path = lesson["embedding"]
                break
        if reference_embedding_path:
            break

    if not reference_embedding_path or not os.path.exists(reference_embedding_path):
        raise HTTPException(status_code=400, detail="Lesson not found or embedding missing")

    user_landmarks = []
    for frame_data in frames[:FRAMES_LIMIT]:
        img_data = base64.b64decode(frame_data.split(',')[1])
        nparr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        landmarks = landmark_service.get_frame_landmarks(frame_rgb)
        user_landmarks.append(landmarks)

    user_embedding = model_service.extract_embedding(user_landmarks)
    reference_embedding = np.load(reference_embedding_path)

    similarity = model_service.calculate_similarity(user_embedding, reference_embedding)
    status = model_service.get_similarity_status(similarity)

    return VideoResponse(similarity=float(similarity), status=status)

@router.get("/")
async def redirect_to_index():
    return RedirectResponse(url="/public/index.html")
