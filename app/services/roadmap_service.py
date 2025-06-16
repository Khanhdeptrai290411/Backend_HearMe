import re
from app.database.connection import execute_query

class RoadmapService:
    def __init__(self, model_service):
        self.model_service = model_service
        # Ánh xạ model_id -> thư mục
        self.model_config = {
            1: {
                "video_dir": "Family_video2",
                "embedding_dir": "Family/reference_embedding2",
            },
            2: {
                "video_dir": "Color_video2",
                "embedding_dir": "Color_model/reference_embedding2",
            }
            # Thêm model khác nếu cần
        }

    def clean_label(self, video_filename):
        raw_label_name = video_filename.split('-')[-1].split('.')[0]
        return re.sub(r'\s*\d+$', '', raw_label_name)

    def get_roadmap(self):
        # Lấy tất cả chapters thuộc model_id = 1
        chapters_query = """
            SELECT id, name, model_id
            FROM chapters
            ORDER BY model_id, id
        """
        chapters = execute_query(chapters_query)

        roadmap = {}
        for chapter in chapters:
            chapter_id = chapter['id']
            chapter_name = chapter['name']
            model_id = chapter['model_id']

            # Lấy cấu hình thư mục tương ứng model_id
            config = self.model_config.get(model_id)
            if not config:
                continue  # bỏ qua nếu không có cấu hình

            videos_query = """
                SELECT id, video_filename
                FROM videos
                WHERE model_id = %s AND chapter_id = %s
                ORDER BY video_filename
            """
            videos = execute_query(videos_query, (model_id, chapter_id))

            chapter_videos = []
            for video in videos:
                video_filename = video['video_filename']
                base = video_filename.split('.')[0]
                label = self.clean_label(video_filename)
                public_path = f"/{config['video_dir']}/{video_filename}".replace("Family/", "")
                embedding_path = f"{config['embedding_dir']}/{base}_embedding.npy"

                chapter_videos.append({
                    "id": video['id'],  # Thêm video_id vào mỗi lesson
                    "name": label,
                    "path": public_path,
                    "embedding": embedding_path,
                    "modelId": model_id
                })

            # Thêm model_id vào tên chương
            roadmap[f"{model_id}-{chapter_name}"] = chapter_videos

        return roadmap 