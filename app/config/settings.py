import os

# Cấu hình cơ bản
FRAMES_LIMIT = 60

# Cấu hình MediaPipe
FILTERED_HAND = list(range(21))
FILTERED_POSE = [11, 12, 13, 14, 15, 16]
FILTERED_FACE = [4, 6, 8, 9, 33, 37, 40, 46, 52, 55, 61, 70, 80, 82, 84, 87, 88, 91,
                 105, 107, 133, 145, 154, 157, 159, 161, 163, 263, 267, 270, 276,
                 282, 285, 291, 300, 310, 312, 314, 317, 318, 321, 334, 336, 362,
                 374, 381, 384, 386, 388, 390, 468, 473]

# Cấu hình database
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "hearme_learning"
}

# Cấu hình thư mục
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PUBLIC_DIR = os.path.join(BASE_DIR, "public") 