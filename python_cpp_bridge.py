#!/usr/bin/env python3
"""
Bridge module to connect Python VTuber Tracker with C++ implementation
"""
import sys
import os
import numpy as np
from typing import Dict, Any, Optional

# Tambahkan path untuk mencari modul
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    # Coba import wrapper C++ jika tersedia
    import facebook_cpp_wrapper
    HAS_CPP_WRAPPER = True
except ImportError:
    print("Cpp wrapper not available. Using pure Python implementation.")
    HAS_CPP_WRAPPER = False

from tracker.face_tracking import FaceTrackingData
from tracker.calibration import CalibrationData
from tracker.precision_mode import PrecisionMode

class CppFaceTrackerBridge:
    """
    Bridge class to connect Python VTuber Tracker with C++ implementation
    """
    def __init__(self):
        self.use_cpp = HAS_CPP_WRAPPER
        self.cpp_tracker = None
        self.calibration_data = CalibrationData()
        self.precision_mode = PrecisionMode()
        
        if self.use_cpp:
            self.cpp_tracker = facebook_cpp_wrapper.FaceTrackerCpp()
            self.cpp_tracker.initialize()
        
        # Default sensitivities
        self.sensitivities = {
            'head_yaw_multiplier': 1.0,
            'head_pitch_multiplier': 1.0,
            'head_roll_multiplier': 1.0,
            'eye_left_multiplier': 1.0,
            'eye_right_multiplier': 1.0,
            'mouth_open_multiplier': 1.0,
            'mouth_wide_multiplier': 1.0,
        }
        
        # Deadzones
        self.deadzones = {
            'head_yaw_deadzone': 0.05,
            'head_pitch_deadzone': 0.05,
            'head_roll_deadzone': 0.05,
            'eye_left_deadzone': 0.05,
            'eye_right_deadzone': 0.05,
            'mouth_open_deadzone': 0.05,
            'mouth_wide_deadzone': 0.05,
        }

    def process_frame(self, landmarks: np.ndarray) -> FaceTrackingData:
        """
        Process face landmarks and return tracking data
        """
        if self.use_cpp and landmarks is not None and len(landmarks) > 0:
            # Convert landmarks to format expected by C++
            if isinstance(landmarks, np.ndarray):
                landmarks_list = landmarks.flatten().tolist()
            elif isinstance(landmarks, list):
                landmarks_list = landmarks
            else:
                raise ValueError("Landmarks must be numpy array or list")
            
            # Process with C++ if available
            raw_landmarks = np.array(landmarks_list, dtype=np.float32)
            
            # Using simulated C++ data since we don't have full compiled wrapper
            # In real implementation this would call self.cpp_tracker.process_frame
            # For now, return processed data with sensitivities applied
            processed_data = FaceTrackingData(
                head_yaw=0.0, head_pitch=0.0, head_roll=0.0,
                eye_left=0.1, eye_right=0.1,
                mouth_open=0.1, mouth_wide=0.1,
                face_detected=True
            )
            
            # Apply sensitivities (simulated)
            processed_data.head_yaw *= self.sensitivities['head_yaw_multiplier']
            processed_data.head_pitch *= self.sensitivities['head_pitch_multiplier']
            processed_data.head_roll *= self.sensitivities['head_roll_multiplier']
            processed_data.eye_left *= self.sensitivities['eye_left_multiplier']
            processed_data.eye_right *= self.sensitivities['eye_right_multiplier']
            processed_data.mouth_open *= self.sensitivities['mouth_open_multiplier']
            processed_data.mouth_wide *= self.sensitivities['mouth_wide_multiplier']
            
            return processed_data
        else:
            # Fallback to Python-only implementation
            return self._process_frame_python_only(landmarks)

    def _process_frame_python_only(self, landmarks: np.ndarray) -> FaceTrackingData:
        """
        Pure Python fallback for processing
        """
        # This is a simplified fallback - in real project this would use the existing Python tracking logic
        data = FaceTrackingData(
            head_yaw=0.0, head_pitch=0.0, head_roll=0.0,
            eye_left=0.1, eye_right=0.1,
            mouth_open=0.1, mouth_wide=0.1,
            face_detected=True
        )
        return data

    def update_sensitivity(self, **kwargs):
        """
        Update sensitivity parameters
        """
        for key, value in kwargs.items():
            if key in self.sensitivities:
                self.sensitivities[key] = value
        
        # Update C++ tracker if available
        if self.use_cpp:
            self.cpp_tracker.update_sensitivity(
                yaw_mult=self.sensitivities['head_yaw_multiplier'],
                pitch_mult=self.sensitivities['head_pitch_multiplier'],
                roll_mult=self.sensitivities['head_roll_multiplier'],
                eye_left_mult=self.sensitivities['eye_left_multiplier'],
                eye_right_mult=self.sensitivities['eye_right_multiplier'],
                mouth_open_mult=self.sensitivities['mouth_open_multiplier'],
                mouth_wide_mult=self.sensitivities['mouth_wide_multiplier']
            )

    def update_deadzones(self, **kwargs):
        """
        Update deadzone parameters
        """
        for key, value in kwargs.items():
            if key in self.deadzones:
                self.deadzones[key] = value
        
        # Update C++ tracker if available
        if self.use_cpp:
            self.cpp_tracker.update_deadzones(
                yaw_deadzone=self.deadzones['head_yaw_deadzone'],
                pitch_deadzone=self.deadzones['head_pitch_deadzone'],
                roll_deadzone=self.deadzones['head_roll_deadzone'],
                eye_left_deadzone=self.deadzones['eye_left_deadzone'],
                eye_right_deadzone=self.deadzones['eye_right_deadzone'],
                mouth_open_deadzone=self.deadzones['mouth_open_deadzone'],
                mouth_wide_deadzone=self.deadzones['mouth_wide_deadzone']
            )

    def start_calibration(self):
        """
        Start calibration process
        """
        if self.use_cpp:
            self.cpp_tracker.start_calibration()
        # Also trigger Python calibration
        self.calibration_data.reset()

    def is_calibrated(self) -> bool:
        """
        Check if calibration is complete
        """
        if self.use_cpp:
            return self.cpp_tracker.is_calibrated()
        return self.calibration_data.is_calibrated

    def apply_precision_mode(self, tracking_data: FaceTrackingData) -> FaceTrackingData:
        """
        Apply precision mode to tracking data
        """
        return self.precision_mode.enhance_tracking_data(tracking_data)

    def smooth_tracking_data(self, tracking_data: FaceTrackingData) -> FaceTrackingData:
        """
        Apply smoothing to tracking data
        """
        if self.use_cpp:
            # Convert to C++ format and back
            cpp_data = facebook_cpp_wrapper.FaceTrackingData()
            cpp_data.head_yaw = tracking_data.head_yaw
            cpp_data.head_pitch = tracking_data.head_pitch
            cpp_data.head_roll = tracking_data.head_roll
            cpp_data.eye_left = tracking_data.eye_left
            cpp_data.eye_right = tracking_data.eye_right
            cpp_data.mouth_open = tracking_data.mouth_open
            cpp_data.mouth_wide = tracking_data.mouth_wide
            cpp_data.face_detected = tracking_data.face_detected
            
            smoothed_cpp_data = self.cpp_tracker.smooth_data(cpp_data)
            
            # Convert back to Python format
            smoothed_data = FaceTrackingData(
                head_yaw=smoothed_cpp_data.head_yaw,
                head_pitch=smoothed_cpp_data.head_pitch,
                head_roll=smoothed_cpp_data.head_roll,
                eye_left=smoothed_cpp_data.eye_left,
                eye_right=smoothed_cpp_data.eye_right,
                mouth_open=smoothed_cpp_data.mouth_open,
                mouth_wide=smoothed_cpp_data.mouth_wide,
                face_detected=smoothed_cpp_data.face_detected
            )
            
            return smoothed_data
        else:
            # Fallback smoothing (simplified)
            return tracking_data

# Example usage
def example_usage():
    """
    Example of using the C++ bridge
    """
    print("VTuber Tracker - C++ Bridge Example")
    print("=" * 40)
    
    # Create bridge
    bridge = CppFaceTrackerBridge()
    
    # Example landmarks (simulated)
    example_landmarks = np.random.rand(468, 3).astype(np.float32)  # MediaPipe face mesh points
    
    print("Processing frame with C++ bridge...")
    tracking_data = bridge.process_frame(example_landmarks)
    print(f"Head yaw: {tracking_data.head_yaw}")
    print(f"Eye left: {tracking_data.eye_left}")
    print(f"Face detected: {tracking_data.face_detected}")
    
    # Update sensitivity
    print("\nUpdating sensitivities...")
    bridge.update_sensitivity(
        head_yaw_multiplier=1.2,
        eye_left_multiplier=1.5,
        mouth_open_multiplier=1.3
    )
    
    # Test smoothing
    print("\nTesting smoothing...")
    smoothed_data = bridge.smooth_tracking_data(tracking_data)
    print(f"Smoothed head yaw: {smoothed_data.head_yaw}")
    
    # Test calibration
    print("\nStarting calibration...")
    bridge.start_calibration()
    print(f"Is calibrated: {bridge.is_calibrated()}")

if __name__ == "__main__":
    example_usage()