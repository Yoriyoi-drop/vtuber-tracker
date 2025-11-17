"""
Face tracking module for VTuber face tracking system.
Uses MediaPipe FaceMesh to detect facial landmarks and extract tracking data.
"""
import cv2
import mediapipe as mp
import numpy as np
import logging
from dataclasses import dataclass
from typing import Optional, Tuple, List
import math

@dataclass
class FaceTrackingData:
    """Data class to hold face tracking results."""
    head_yaw: float = 0.0
    head_pitch: float = 0.0
    head_roll: float = 0.0
    eye_left: float = 0.0
    eye_right: float = 0.0
    mouth_open: float = 0.0
    mouth_wide: float = 0.0
    face_detected: bool = False

class FaceTracker:
    def __init__(self, max_num_faces=1, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.max_num_faces = max_num_faces
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        
        # Initialize MediaPipe FaceMesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=self.max_num_faces,
            refine_landmarks=True,
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence
        )
        
        # Face landmark indices
        # Eyes
        self.LEFT_EYE_INNER = [386, 374, 385, 380, 381, 382]  # Right eye in image (left from person's perspective)
        self.RIGHT_EYE_INNER = [159, 145, 158, 153, 154, 155]  # Left eye in image (right from person's perspective)
        self.LEFT_EYE_OUTER = [263, 249, 260, 255, 256, 257]
        self.RIGHT_EYE_OUTER = [33, 11, 229, 230, 231, 244]
        
        # Mouth
        self.MOUTH_UPPER_LIP = [13, 14, 15, 16, 0, 17, 18, 19, 20]
        self.MOUTH_LOWER_LIP = [78, 80, 81, 82, 13, 14, 15, 16]
        self.MOUTH_LEFT_CORNER = 61
        self.MOUTH_RIGHT_CORNER = 291
        
        # Face contour for head pose estimation
        self.NOSE_TIP = 1
        self.NOSE_CENTER = 168
        self.LEFT_EAR = 127
        self.RIGHT_EAR = 356
        self.CHIN = 152
        self.FOREHEAD = 10
        
        # Initialize previous data for smoothing
        self.prev_tracking_data = FaceTrackingData()
    
    def get_landmarks(self, image):
        """Get face landmarks from image."""
        # Convert the BGR image to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process the image and find face landmarks
        results = self.face_mesh.process(rgb_image)
        
        return results
    
    def calculate_head_rotation(self, landmarks, image_shape) -> Tuple[float, float, float]:
        """Calculate head rotation (yaw, pitch, roll) from face landmarks."""
        h, w = image_shape[:2]
        
        # Get specific landmarks for pose estimation
        try:
            # Define 3D points for pose estimation
            # These are standard points for face pose estimation
            model_points = np.array([
                (0.0, 0.0, 0.0),             # Nose tip
                (0.0, -300.0, -300.0),      # Chin
                (-225.0, 170.0, -135.0),    # Left eye left corner
                (225.0, 170.0, -135.0),     # Right eye right corne
                (-150.0, -150.0, -125.0),   # Left Mouth corner
                (150.0, -150.0, -125.0)     # Right mouth corner
            ])
            
            # Image points from landmarks
            image_points = np.array([
                (landmarks[self.NOSE_TIP].x * w, landmarks[self.NOSE_TIP].y * h),  # Nose tip
                (landmarks[self.CHIN].x * w, landmarks[self.CHIN].y * h),  # Chin
                (landmarks[33].x * w, landmarks[33].y * h),  # Left eye left corner
                (landmarks[263].x * w, landmarks[263].y * h),  # Right eye right corner
                (landmarks[61].x * w, landmarks[61].y * h),  # Left mouth corner
                (landmarks[291].x * w, landmarks[291].y * h)  # Right mouth corner
            ], dtype="double")
            
            # Camera matrix
            focal_length = w
            center = (w / 2, h / 2)
            camera_matrix = np.array([
                [focal_length, 0, center[0]],
                [0, focal_length, center[1]],
                [0, 0, 1]
            ], dtype="double")
            
            # Distortion coefficients
            dist_coeffs = np.zeros((4, 1))
            
            # Solve PnP to get rotation and translation vectors
            success, rotation_vector, translation_vector = cv2.solvePnP(
                model_points, 
                image_points, 
                camera_matrix, 
                dist_coeffs
            )
            
            if success:
                # Convert rotation vector to rotation matrix
                rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
                
                # Convert to Euler angles
                # Get Euler angles from rotation matrix
                sy = math.sqrt(rotation_matrix[0,0] * rotation_matrix[0,0] + 
                              rotation_matrix[1,0] * rotation_matrix[1,0])
                
                singular = sy < 1e-6
                
                if not singular:
                    x = math.atan2(rotation_matrix[2,1], rotation_matrix[2,2])
                    y = math.atan2(-rotation_matrix[2,0], sy)
                    z = math.atan2(rotation_matrix[1,0], rotation_matrix[0,0])
                else:
                    x = math.atan2(-rotation_matrix[1,2], rotation_matrix[1,1])
                    y = math.atan2(-rotation_matrix[2,0], sy)
                    z = 0
                
                # Convert to degrees and scale for better sensitivity
                yaw = np.clip(np.degrees(y), -30, 30) / 30.0  # Normalize to [-1, 1]
                pitch = np.clip(np.degrees(x), -30, 30) / 30.0  # Normalize to [-1, 1]
                roll = np.clip(np.degrees(z), -30, 30) / 30.0  # Normalize to [-1, 1]
                
                return yaw, pitch, roll
            else:
                return 0.0, 0.0, 0.0
                
        except Exception as e:
            logging.warning(f"Error calculating head rotation: {e}")
            return 0.0, 0.0, 0.0
    
    def calculate_eye_blink(self, landmarks, eye_indices) -> float:
        """Calculate eye blink value based on eye landmark distances."""
        try:
            # Get eye landmarks
            eye_landmarks = [landmarks[i] for i in eye_indices]
            
            # Calculate vertical eye aspect ratio (EAR)
            # Distance between upper and lower eyelid
            vertical_dist = np.linalg.norm(
                np.array([eye_landmarks[1].x, eye_landmarks[1].y]) - 
                np.array([eye_landmarks[5].x, eye_landmarks[5].y])
            )
            
            # Distance between left and right eyelid
            horizontal_dist = np.linalg.norm(
                np.array([eye_landmarks[0].x, eye_landmarks[0].y]) - 
                np.array([eye_landmarks[4].x, eye_landmarks[4].y])
            )
            
            # Calculate eye aspect ratio
            if horizontal_dist > 0:
                ear = vertical_dist / horizontal_dist
                # Normalize to roughly [0, 1] range where 0 is fully open and 1 is closed
                # Typical open eye has EAR ~0.3, closed eye has EAR ~0.15
                normalized_value = max(0, min(1, (0.3 - ear) / 0.15))
                return normalized_value
            else:
                return 0.0
        except Exception as e:
            logging.warning(f"Error calculating eye blink: {e}")
            return 0.0
    
    def calculate_mouth_open(self, landmarks) -> float:
        """Calculate mouth open value based on upper-lower lip distance."""
        try:
            # Get upper and lower lip landmarks
            upper_lip_points = [landmarks[i] for i in self.MOUTH_UPPER_LIP]
            lower_lip_points = [landmarks[i] for i in self.MOUTH_LOWER_LIP]
            
            # Calculate average vertical distance between upper and lower lips
            upper_avg = np.mean([[p.x, p.y] for p in upper_lip_points], axis=0)
            lower_avg = np.mean([[p.x, p.y] for p in lower_lip_points], axis=0)
            
            vertical_dist = abs(upper_avg[1] - lower_avg[1])
            
            # Normalize to [0, 1] range
            # Typical closed mouth has vertical dist ~0.02, open mouth ~0.08
            normalized_value = max(0, min(1, (vertical_dist - 0.02) / 0.06))
            return normalized_value
        except Exception as e:
            logging.warning(f"Error calculating mouth open: {e}")
            return 0.0
    
    def calculate_mouth_wide(self, landmarks) -> float:
        """Calculate mouth width/smile based on corner distance."""
        try:
            # Get mouth corner landmarks
            left_corner = landmarks[self.MOUTH_LEFT_CORNER]
            right_corner = landmarks[self.MOUTH_RIGHT_CORNER]
            
            # Calculate horizontal distance between mouth corners
            corner_dist = np.linalg.norm(
                np.array([left_corner.x, left_corner.y]) - 
                np.array([right_corner.x, right_corner.y])
            )
            
            # Compare to neutral mouth width (typical neutral width is around 0.1-0.15 in normalized coords)
            # Smiling increases this distance
            normalized_value = max(0, min(1, (corner_dist - 0.1) / 0.1))
            return normalized_value
        except Exception as e:
            logging.warning(f"Error calculating mouth wide: {e}")
            return 0.0
    
    def process_frame(self, image) -> FaceTrackingData:
        """Process a single frame and extract face tracking data."""
        h, w = image.shape[:2]
        
        # Get face landmarks
        results = self.get_landmarks(image)
        
        if not results.multi_face_landmarks:
            # No face detected
            return FaceTrackingData(face_detected=False)
        
        # Get the first face (we only track one face)
        face_landmarks = results.multi_face_landmarks[0]
        landmarks = face_landmarks.landmark
        
        # Calculate all tracking parameters
        yaw, pitch, roll = self.calculate_head_rotation(landmarks, image.shape)
        
        # Calculate eye blinks
        left_eye_blink = self.calculate_eye_blink(landmarks, self.LEFT_EYE_INNER)
        right_eye_blink = self.calculate_eye_blink(landmarks, self.RIGHT_EYE_INNER)
        
        # Calculate mouth parameters
        mouth_open = self.calculate_mouth_open(landmarks)
        mouth_wide = self.calculate_mouth_wide(landmarks)
        
        # Create tracking data object
        tracking_data = FaceTrackingData(
            head_yaw=yaw,
            head_pitch=pitch,
            head_roll=roll,
            eye_left=left_eye_blink,
            eye_right=right_eye_blink,
            mouth_open=mouth_open,
            mouth_wide=mouth_wide,
            face_detected=True
        )
        
        return tracking_data
    
    def draw_landmarks(self, image, results):
        """Draw face landmarks on image for visualization."""
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                self.mp_drawing.draw_landmarks(
                    image,
                    face_landmarks,
                    self.mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing_styles
                    .get_default_face_mesh_tesselation_style())
                self.mp_drawing.draw_landmarks(
                    image,
                    face_landmarks,
                    self.mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing_styles
                    .get_default_face_mesh_contours_style())
        
        return image
    
    def release(self):
        """Release MediaPipe resources."""
        if self.face_mesh:
            self.face_mesh.close()