from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .api import course, dictionary, user, routes
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os

from app.models.flashcard import Course, Quiz  # Import Course và Quiz sau
from app.api.routes import router
from app.api.endpoints import flashcard, auth

app = FastAPI()

# Create uploads directory if it doesn't exist
os.makedirs("public/uploads", exist_ok=True)

# Configure CORS - allow all origins during development
origins = [
    "http://localhost:5173",    # Vite dev server
    "http://localhost:3000",    # Alternative React port
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Add middleware to log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Request path: {request.url.path}")
    response = await call_next(request)
    return response

# Mount the static files directory
app.mount("/public", StaticFiles(directory="public", html=True, check_dir=True), name="public")

# Add a test endpoint
@app.get("/test-static")
async def test_static():
    # List all files in public/uploads
    files = os.listdir("public/uploads")
    return JSONResponse({
        "message": "Static files directory content",
        "files": files,
        "public_dir_exists": os.path.exists("public"),
        "uploads_dir_exists": os.path.exists("public/uploads")
    })

# Include API routes

app.include_router(course.router, prefix="/api/course", tags=["course"])
app.include_router(dictionary.router, prefix="/api/dictionary", tags=["dictionary"])
app.include_router(user.router, prefix="/api/users", tags=["users"])
app.include_router(routes.router, prefix="/api", tags=["lesson"])
app.include_router(router, prefix="/api")
app.include_router(flashcard.router, prefix="/api/v1", tags=["flashcard"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
