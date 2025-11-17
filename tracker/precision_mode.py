"""
Precision mode module for VTuber face tracking system.
Provides high-precision tracking for detailed facial expressions.
"""
from .face_tracking import FaceTrackingData
import numpy as np
import logging

class PrecisionMode:
    """
    Class to handle high-precision tracking mode.
    Applies more sensitive detection and processing for subtle facial movements.
    """
    def __init__(self):
        self.enabled = False
        self.sensitivity_multiplier = 1.5  # Default multiplier for precision mode
        self.prev_data = None
        self.noise_reduction_enabled = True
        self.noise_threshold = 0.01  # Threshold for minor fluctuations
        
        # Additional precision parameters
        self.eye_blink_precision = True
        self.mouth_precision = True
        self.head_rotation_precision = True

    def enable_precision_mode(self, multiplier=1.5):
        """
        Enable precision mode with specified sensitivity multiplier.
        
        Args:
            multiplier: Sensitivity multiplier (default 1.5 for moderate precision increase)
        """
        self.enabled = True
        self.sensitivity_multiplier = multiplier
        logging.info(f"Precision mode enabled with multiplier: {multiplier}")

    def disable_precision_mode(self):
        """Disable precision mode."""
        self.enabled = False
        logging.info("Precision mode disabled")

    def enhance_tracking_data(self, raw_data: FaceTrackingData) -> FaceTrackingData:
        """
        Enhance tracking data when precision mode is enabled.
        
        Args:
            raw_data: Raw tracking data from the face tracker
            
        Returns:
            Enhanced tracking data with precision improvements
        """
        if not self.enabled:
            return raw_data

        # Apply sensitivity multiplier to relevant parameters
        enhanced_data = FaceTrackingData(
            head_yaw=raw_data.head_yaw * self.sensitivity_multiplier if self.head_rotation_precision else raw_data.head_yaw,
            head_pitch=raw_data.head_pitch * self.sensitivity_multiplier if self.head_rotation_precision else raw_data.head_pitch,
            head_roll=raw_data.head_roll * self.sensitivity_multiplier if self.head_rotation_precision else raw_data.head_roll,
            eye_left=raw_data.eye_left * self.sensitivity_multiplier if self.eye_blink_precision else raw_data.eye_left,
            eye_right=raw_data.eye_right * self.sensitivity_multiplier if self.eye_blink_precision else raw_data.eye_right,
            mouth_open=raw_data.mouth_open * self.sensitivity_multiplier if self.mouth_precision else raw_data.mouth_open,
            mouth_wide=raw_data.mouth_wide * self.sensitivity_multiplier if self.mouth_precision else raw_data.mouth_wide,
            face_detected=raw_data.face_detected
        )

        # Apply noise reduction if enabled
        if self.noise_reduction_enabled and self.prev_data is not None:
            enhanced_data = self.reduce_noise(enhanced_data, self.prev_data)

        # Ensure values stay within valid range [0, 1] for eye and mouth values
        enhanced_data.eye_left = max(0.0, min(1.0, enhanced_data.eye_left))
        enhanced_data.eye_right = max(0.0, min(1.0, enhanced_data.eye_right))
        enhanced_data.mouth_open = max(0.0, min(1.0, enhanced_data.mouth_open))
        enhanced_data.mouth_wide = max(0.0, min(1.0, enhanced_data.mouth_wide))

        # For head rotations, keep within [-1, 1] range
        enhanced_data.head_yaw = max(-1.0, min(1.0, enhanced_data.head_yaw))
        enhanced_data.head_pitch = max(-1.0, min(1.0, enhanced_data.head_pitch))
        enhanced_data.head_roll = max(-1.0, min(1.0, enhanced_data.head_roll))

        # Store for next iteration
        self.prev_data = enhanced_data

        return enhanced_data

    def reduce_noise(self, current_data: FaceTrackingData, prev_data: FaceTrackingData) -> FaceTrackingData:
        """
        Apply noise reduction to minimize small fluctuations.
        
        Args:
            current_data: Current tracking data
            prev_data: Previous tracking data
            
        Returns:
            Tracking data with noise reduction applied
        """
        if not self.noise_reduction_enabled:
            return current_data

        # Calculate differences from previous frame
        yaw_diff = abs(current_data.head_yaw - prev_data.head_yaw)
        pitch_diff = abs(current_data.head_pitch - prev_data.head_pitch)
        roll_diff = abs(current_data.head_roll - prev_data.head_roll)
        eye_left_diff = abs(current_data.eye_left - prev_data.eye_left)
        eye_right_diff = abs(current_data.eye_right - prev_data.eye_right)
        mouth_open_diff = abs(current_data.mouth_open - prev_data.mouth_open)
        mouth_wide_diff = abs(current_data.mouth_wide - prev_data.mouth_wide)

        # Apply noise reduction if the movement is below threshold
        enhanced_data = FaceTrackingData(
            head_yaw=current_data.head_yaw if yaw_diff >= self.noise_threshold else prev_data.head_yaw,
            head_pitch=current_data.head_pitch if pitch_diff >= self.noise_threshold else prev_data.head_pitch,
            head_roll=current_data.head_roll if roll_diff >= self.noise_threshold else prev_data.head_roll,
            eye_left=current_data.eye_left if eye_left_diff >= self.noise_threshold else prev_data.eye_left,
            eye_right=current_data.eye_right if eye_right_diff >= self.noise_threshold else prev_data.eye_right,
            mouth_open=current_data.mouth_open if mouth_open_diff >= self.noise_threshold else prev_data.mouth_open,
            mouth_wide=current_data.mouth_wide if mouth_wide_diff >= self.noise_threshold else prev_data.mouth_wide,
            face_detected=current_data.face_detected
        )

        return enhanced_data

    def set_precision_params(self,
                           sensitivity_multiplier=None,
                           noise_reduction_enabled=None,
                           noise_threshold=None,
                           eye_blink_precision=None,
                           mouth_precision=None,
                           head_rotation_precision=None):
        """
        Set parameters for precision mode.
        
        Args:
            sensitivity_multiplier: Multiplier for sensitivity
            noise_reduction_enabled: Whether noise reduction is enabled
            noise_threshold: Threshold for noise reduction
            eye_blink_precision: Whether to apply precision to eye blinks
            mouth_precision: Whether to apply precision to mouth movements
            head_rotation_precision: Whether to apply precision to head rotations
        """
        if sensitivity_multiplier is not None:
            self.sensitivity_multiplier = sensitivity_multiplier
        if noise_reduction_enabled is not None:
            self.noise_reduction_enabled = noise_reduction_enabled
        if noise_threshold is not None:
            self.noise_threshold = noise_threshold
        if eye_blink_precision is not None:
            self.eye_blink_precision = eye_blink_precision
        if mouth_precision is not None:
            self.mouth_precision = mouth_precision
        if head_rotation_precision is not None:
            self.head_rotation_precision = head_rotation_precision

        logging.info(f"Precision mode parameters updated: "
                    f"multiplier={self.sensitivity_multiplier}, "
                    f"noise_reduction={self.noise_reduction_enabled}, "
                    f"threshold={self.noise_threshold}")


if __name__ == "__main__":
    # Test precision mode
    from .face_tracking import FaceTrackingData

    print("Testing Precision Mode...")

    precision = PrecisionMode()
    
    # Create test data
    test_data = FaceTrackingData(
        head_yaw=0.1,
        head_pitch=0.05,
        head_roll=0.02,
        eye_left=0.1,
        eye_right=0.15,
        mouth_open=0.2,
        mouth_wide=0.15,
        face_detected=True
    )

    print("Original data:")
    print(f"  Head Yaw: {test_data.head_yaw:.3f}")
    print(f"  Eye Left: {test_data.eye_left:.3f}")
    print(f"  Mouth Open: {test_data.mouth_open:.3f}")

    # Test without precision mode
    result1 = precision.enhance_tracking_data(test_data)
    print("\nWithout precision mode:")
    print(f"  Head Yaw: {result1.head_yaw:.3f}")
    print(f"  Eye Left: {result1.eye_left:.3f}")
    print(f"  Mouth Open: {result1.mouth_open:.3f}")

    # Enable precision mode
    precision.enable_precision_mode(multiplier=2.0)
    result2 = precision.enhance_tracking_data(test_data)
    print("\nWith precision mode (multiplier=2.0):")
    print(f"  Head Yaw: {result2.head_yaw:.3f}")
    print(f"  Eye Left: {result2.eye_left:.3f}")
    print(f"  Mouth Open: {result2.mouth_open:.3f}")