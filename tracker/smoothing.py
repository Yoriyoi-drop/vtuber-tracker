"""
Smoothing module for VTuber face tracking system.
Applies smoothing to face tracking data to reduce jitter and noise.
"""
import numpy as np
from .face_tracking import FaceTrackingData
import logging

class DataSmoother:
    def __init__(self, alpha=0.2, enabled=True):
        """
        Initialize the data smoother.
        
        Args:
            alpha: Smoothing factor (0.0 to 1.0). Lower values = more smoothing.
            enabled: Whether smoothing is enabled.
        """
        self.alpha = alpha
        self.enabled = enabled
        self.prev_data = None
        self.initialized = False
        
    def smooth_data(self, current_data: FaceTrackingData) -> FaceTrackingData:
        """
        Apply smoothing to the current tracking data.
        
        Args:
            current_data: Current face tracking data
            
        Returns:
            Smoothed face tracking data
        """
        if not self.enabled or not current_data.face_detected:
            return current_data
        
        if not self.initialized:
            # Use the first frame as the initial value
            self.prev_data = current_data
            self.initialized = True
            return current_data
        
        # Apply exponential moving average (EMA) smoothing
        smoothed_data = FaceTrackingData(
            head_yaw=self._ema(self.prev_data.head_yaw, current_data.head_yaw),
            head_pitch=self._ema(self.prev_data.head_pitch, current_data.head_pitch),
            head_roll=self._ema(self.prev_data.head_roll, current_data.head_roll),
            eye_left=self._ema(self.prev_data.eye_left, current_data.eye_left),
            eye_right=self._ema(self.prev_data.eye_right, current_data.eye_right),
            mouth_open=self._ema(self.prev_data.mouth_open, current_data.mouth_open),
            mouth_wide=self._ema(self.prev_data.mouth_wide, current_data.mouth_wide),
            face_detected=current_data.face_detected
        )
        
        # Update previous data
        self.prev_data = smoothed_data
        
        return smoothed_data
    
    def _ema(self, prev_value: float, current_value: float) -> float:
        """
        Calculate Exponential Moving Average.
        
        Args:
            prev_value: Previous smoothed value
            current_value: Current raw value
            
        Returns:
            Smoothed value
        """
        return self.alpha * current_value + (1 - self.alpha) * prev_value
    
    def reset(self):
        """Reset the smoother to initial state."""
        self.prev_data = None
        self.initialized = False
    
    def update_alpha(self, new_alpha: float):
        """
        Update the smoothing factor.
        
        Args:
            new_alpha: New smoothing factor (0.0 to 1.0)
        """
        self.alpha = max(0.0, min(1.0, new_alpha))
        logging.info(f"Smoothing alpha updated to {self.alpha}")

class AdvancedSmoother:
    """
    More advanced smoothing that can apply different smoothing factors 
    to different types of data (e.g., head rotation vs eye blinks).
    """
    def __init__(self, 
                 head_rotation_alpha=0.1, 
                 eye_blink_alpha=0.3, 
                 mouth_alpha=0.2,
                 enabled=True):
        """
        Initialize the advanced data smoother.
        
        Args:
            head_rotation_alpha: Smoothing for head rotation (yaw, pitch, roll)
            eye_blink_alpha: Smoothing for eye blink data
            mouth_alpha: Smoothing for mouth data
            enabled: Whether smoothing is enabled
        """
        self.head_rotation_alpha = head_rotation_alpha
        self.eye_blink_alpha = eye_blink_alpha
        self.mouth_alpha = mouth_alpha
        self.enabled = enabled
        self.prev_data = None
        self.initialized = False
    
    def smooth_data(self, current_data: FaceTrackingData) -> FaceTrackingData:
        """
        Apply advanced smoothing to the current tracking data.
        
        Args:
            current_data: Current face tracking data
            
        Returns:
            Smoothed face tracking data
        """
        if not self.enabled or not current_data.face_detected:
            return current_data
        
        if not self.initialized:
            # Use the first frame as the initial value
            self.prev_data = current_data
            self.initialized = True
            return current_data
        
        # Apply different smoothing factors to different data types
        smoothed_data = FaceTrackingData(
            head_yaw=self._ema(self.prev_data.head_yaw, current_data.head_yaw, self.head_rotation_alpha),
            head_pitch=self._ema(self.prev_data.head_pitch, current_data.head_pitch, self.head_rotation_alpha),
            head_roll=self._ema(self.prev_data.head_roll, current_data.head_roll, self.head_rotation_alpha),
            eye_left=self._ema(self.prev_data.eye_left, current_data.eye_left, self.eye_blink_alpha),
            eye_right=self._ema(self.prev_data.eye_right, current_data.eye_right, self.eye_blink_alpha),
            mouth_open=self._ema(self.prev_data.mouth_open, current_data.mouth_open, self.mouth_alpha),
            mouth_wide=self._ema(self.prev_data.mouth_wide, current_data.mouth_wide, self.mouth_alpha),
            face_detected=current_data.face_detected
        )
        
        # Update previous data
        self.prev_data = smoothed_data
        
        return smoothed_data
    
    def _ema(self, prev_value: float, current_value: float, alpha: float) -> float:
        """
        Calculate Exponential Moving Average with custom alpha.
        
        Args:
            prev_value: Previous smoothed value
            current_value: Current raw value
            alpha: Smoothing factor for this specific data type
            
        Returns:
            Smoothed value
        """
        return alpha * current_value + (1 - alpha) * prev_value
    
    def reset(self):
        """Reset the smoother to initial state."""
        self.prev_data = None
        self.initialized = False
    
    def update_params(self, head_rotation_alpha=None, eye_blink_alpha=None, mouth_alpha=None):
        """Update smoothing parameters."""
        if head_rotation_alpha is not None:
            self.head_rotation_alpha = max(0.0, min(1.0, head_rotation_alpha))
        if eye_blink_alpha is not None:
            self.eye_blink_alpha = max(0.0, min(1.0, eye_blink_alpha))
        if mouth_alpha is not None:
            self.mouth_alpha = max(0.0, min(1.0, mouth_alpha))
        
        logging.info(f"Advanced smoother params updated - "
                    f"head: {self.head_rotation_alpha}, "
                    f"eyes: {self.eye_blink_alpha}, "
                    f"mouth: {self.mouth_alpha}")

if __name__ == "__main__":
    # Test the smoothing module
    from .face_tracking import FaceTrackingData
    
    smoother = DataSmoother(alpha=0.3)
    
    # Simulate some tracking data
    test_data = [
        FaceTrackingData(head_yaw=0.1, head_pitch=0.05, eye_left=0.0, eye_right=0.0, mouth_open=0.0),
        FaceTrackingData(head_yaw=0.12, head_pitch=0.06, eye_left=0.0, eye_right=0.0, mouth_open=0.0),
        FaceTrackingData(head_yaw=0.09, head_pitch=0.03, eye_left=0.0, eye_right=0.0, mouth_open=0.0),
        FaceTrackingData(head_yaw=0.11, head_pitch=0.07, eye_left=0.0, eye_right=0.0, mouth_open=0.0),
        FaceTrackingData(head_yaw=0.10, head_pitch=0.04, eye_left=0.0, eye_right=0.0, mouth_open=0.0),
    ]
    
    print("Raw data vs Smoothed data:")
    for i, data in enumerate(test_data):
        smoothed = smoother.smooth_data(data)
        print(f"Frame {i+1}: Raw Yaw={data.head_yaw:.3f}, Smoothed Yaw={smoothed.head_yaw:.3f}")