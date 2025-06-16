import numpy as np
import mediapipe as mp
from app.config.settings import FILTERED_HAND, FILTERED_POSE, FILTERED_FACE

class LandmarkService:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_pose = mp.solutions.pose
        self.mp_face = mp.solutions.face_mesh
        
        self.hands = self.mp_hands.Hands(False, max_num_hands=2, min_detection_confidence=0.5)
        self.pose = self.mp_pose.Pose(False, min_detection_confidence=0.5)
        self.face_mesh = self.mp_face.FaceMesh(False, max_num_faces=1, min_detection_confidence=0.5, refine_landmarks=True)
        
        self.HAND_NUM = len(FILTERED_HAND)
        self.POSE_NUM = len(FILTERED_POSE)
        self.FACE_NUM = len(FILTERED_FACE)

    def get_frame_landmarks(self, frame):
        all_landmarks = np.zeros((self.HAND_NUM * 2 + self.POSE_NUM + self.FACE_NUM, 3))

        results_hands = self.hands.process(frame)
        if results_hands.multi_hand_landmarks:
            for i, hand_landmarks in enumerate(results_hands.multi_hand_landmarks):
                index = 0 if results_hands.multi_handedness[i].classification[0].index == 0 else self.HAND_NUM
                all_landmarks[index:index+self.HAND_NUM, :] = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]

        results_pose = self.pose.process(frame)
        if results_pose.pose_landmarks:
            all_landmarks[self.HAND_NUM * 2:self.HAND_NUM * 2 + self.POSE_NUM, :] = np.array(
                [(lm.x, lm.y, lm.z) for lm in results_pose.pose_landmarks.landmark])[FILTERED_POSE]

        results_face = self.face_mesh.process(frame)
        if results_face.multi_face_landmarks:
            all_landmarks[self.HAND_NUM * 2 + self.POSE_NUM:, :] = np.array(
                [(lm.x, lm.y, lm.z) for lm in results_face.multi_face_landmarks[0].landmark])[FILTERED_FACE]

        return all_landmarks 