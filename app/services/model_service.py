import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.metrics import CosineSimilarity
from app.database.connection import execute_query
from datetime import datetime
from fastapi import Request

class ModelService:
    def __init__(self):
        self.model = None
        self.config = None
        self.load_config_and_model()

    def load_config_and_model(self, model_id=1):
        query = """
            SELECT model_file, embedding_dir, threshold, target_shape
            FROM models
            WHERE id = %s
        """
        config = execute_query(query, (model_id,), fetch_one=True)
        if not config:
            raise Exception(f"Model with ID {model_id} not found in database")

        target_shape_str = config['target_shape'].strip("()").replace(" ", "")
        try:
            target_shape = tuple(int(x) for x in target_shape_str.split(","))
        except ValueError as e:
            raise Exception(f"Invalid target_shape format: {str(e)}")

        self.config = {
            "model_file": config['model_file'],
            "embedding_dir": config['embedding_dir'],
            "threshold": float(config['threshold']),
            "target_shape": target_shape
        }

        try:
            print(f"Loading model from: {self.config['model_file']}")
            self.model = load_model(self.config['model_file'])
        except Exception as e:
            raise Exception(f"Error loading model file: {str(e)}")

    def extract_embedding(self, video_landmarks):
        video_landmarks = np.array(video_landmarks)
        target_shape = self.config['target_shape']
        
        if video_landmarks.shape[0] < target_shape[0]:
            padding = target_shape[0] - video_landmarks.shape[0]
            video_landmarks = np.pad(video_landmarks, ((0, padding), (0, 0), (0, 0)), mode='constant')
        else:
            video_landmarks = video_landmarks[:target_shape[0], :, :]
            
        video_landmarks = np.reshape(video_landmarks, (1, *target_shape))
        return self.model.predict(video_landmarks)

    def calculate_similarity(self, embedding1, embedding2):
        cosine_similarity = CosineSimilarity()
        similarity = cosine_similarity(embedding1, embedding2)
        return float(similarity.numpy())

    def get_similarity_status(self, similarity, user_id: int = None, video_id: int = None):
        threshold = self.config['threshold']
        status = "Match!" if similarity >= threshold else "Not Match"
        
        print(f"Checking match with threshold {threshold}: similarity={similarity}, status={status}")
        print(f"User ID: {user_id}, Video ID: {video_id}")
        
        if status == "Match!" and user_id is not None and video_id is not None:
            try:
                print(f"Attempting to save progress for user {user_id} on video {video_id}")
                insert_progress = """
                    INSERT INTO user_video_progress (user_id, video_id, is_completed, completed_at)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE is_completed = VALUES(is_completed), completed_at = VALUES(completed_at)
                """
                current_time = datetime.utcnow()
                params = (user_id, video_id, True, current_time)
                print(f"Executing query with params: {params}")
                
                result = execute_query(insert_progress, params)
                print(f"Query executed. Result: {result}")
                
                # Verify if the record was actually saved
                verify_query = """
                    SELECT * FROM user_video_progress 
                    WHERE user_id = %s AND video_id = %s
                """
                verify_result = execute_query(verify_query, (user_id, video_id), fetch_one=True)
                print(f"Verification query result: {verify_result}")
                
                if verify_result:
                    print(f"Progress saved and verified for user {user_id} on video {video_id}")
                else:
                    print(f"Warning: Progress may not have been saved correctly")
                    
            except Exception as e:
                print(f"Error saving progress: {str(e)}")
                print(f"Error type: {type(e)}")
                import traceback
                print(f"Full traceback: {traceback.format_exc()}")
                # Continue with returning status even if saving progress fails
                
        return status 