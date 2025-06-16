import os
import base64
import numpy as np
import cv2
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from app.models.schemas import VideoProcessRequest, VideoResponse
from app.services.landmark_service import LandmarkService
from app.services.model_service import ModelService
from app.services.roadmap_service import RoadmapService
from app.config.settings import FRAMES_LIMIT
from .user import router as user_router
from .course import router as course_router
from app.core.deps import get_current_active_user, get_current_user_optional  # Import optional authentication

router = APIRouter()
landmark_service = LandmarkService()
model_service = ModelService()
roadmap_service = RoadmapService(model_service)

router.include_router(user_router, tags=["users"])
router.include_router(course_router, prefix="/course", tags=["courses"])


@router.get("/roadmap")
async def get_roadmap():
    """Lấy danh sách các chương và bài học"""
    return roadmap_service.get_roadmap()

@router.post("/process-video", response_model=VideoResponse)
async def process_video(
    request: VideoProcessRequest,
    current_user: dict = Depends(get_current_user_optional)  # Make authentication optional
):
    """
    Xử lý video từ người dùng và so sánh với video mẫu
    - frames: Danh sách các frame dạng base64
    - lessonPath: Đường dẫn đến bài học cần so sánh
    - modelId: ID của model cần sử dụng
    """
    frames = request.frames
    lesson_path = request.lessonPath
    model_id = request.modelId

    # Log authentication status
    if current_user:
        print(f"Processing video for authenticated user: {current_user['email']}")
    else:
        print("Processing video for unauthenticated user")

    print(f"Processing video request - Model ID: {model_id}, Lesson Path: {lesson_path}")

    # Load model configuration cho model_id tương ứng
    try:
        model_service.load_config_and_model(model_id)
        print(f"Loaded model configuration for model {model_id}")
    except Exception as e:
        print(f"Error loading model configuration: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error loading model: {str(e)}")

    # Tìm embedding path từ roadmap
    roadmap = roadmap_service.get_roadmap()
    print(f"Available chapters in roadmap: {list(roadmap.keys())}")
    
    reference_embedding_path = None
    video_id = None
    # Tìm bài học trong roadmap với model_id tương ứng
    for chapter_key, chapter in roadmap.items():
        chapter_model_id = int(chapter_key.split('-')[0])
        print(f"Checking chapter {chapter_key} (model_id: {chapter_model_id})")
        if chapter_model_id == model_id:
            for lesson in chapter:
                print(f"Checking lesson path: {lesson['path']} against {lesson_path}")
                print(f"Lesson data: {lesson}")  # Print full lesson data
                if lesson["path"] == lesson_path:
                    reference_embedding_path = lesson["embedding"]
                    video_id = lesson.get("id")  # Lấy video_id từ lesson
                    print(f"Found embedding path: {reference_embedding_path}")
                    print(f"Found video_id: {video_id}")  # Print video_id
                    break
            if reference_embedding_path:
                break

    if not reference_embedding_path:
        print(f"No embedding path found for lesson {lesson_path} in model {model_id}")
        raise HTTPException(status_code=400, detail="Lesson not found or embedding missing")

    if not os.path.exists(reference_embedding_path):
        print(f"Embedding file not found at path: {reference_embedding_path}")
        raise HTTPException(status_code=400, detail="Embedding file not found")

    # Xử lý frames từ client
    user_landmarks = []
    for frame_data in frames[:FRAMES_LIMIT]:
        img_data = base64.b64decode(frame_data.split(',')[1])
        nparr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        landmarks = landmark_service.get_frame_landmarks(frame_rgb)
        user_landmarks.append(landmarks)

    # Tạo embedding từ video của người dùng
    user_embedding = model_service.extract_embedding(user_landmarks)
    reference_embedding = np.load(reference_embedding_path)

    # Tính độ tương đồng
    similarity = model_service.calculate_similarity(user_embedding, reference_embedding)
    
    # Lấy user_id từ current_user nếu có
    user_id = current_user["id"] if current_user else None
    print(f"Authentication status:")
    print(f"- Current user: {current_user}")
    print(f"- User ID: {user_id}")
    print(f"- Video ID: {video_id}")
    
    status = model_service.get_similarity_status(similarity, user_id, video_id)

    print(f"Video processing complete - Similarity: {similarity}, Status: {status}")
    return VideoResponse(similarity=float(similarity), status=status)

# Thêm route mới để điều hướng
# @router.get("/dictionary")
# async def redirect_to_dictionary():
#     """Điều hướng từ /dictionary đến API dictionary"""
#     return RedirectResponse(url="/api/words")

@router.get("/")
async def redirect_to_index():
    return RedirectResponse(url="/public/index.html") 