"""
Calibration module for VTuber face tracking system.
Provides face calibration functionality to set neutral face position.
"""
from .face_tracking import FaceTrackingData
import numpy as np
import logging

class CalibrationData:
    """
    Data class to hold calibration values.
    """
    def __init__(self):
        # Initialize with default values (no offset)
        self.head_yaw_offset = 0.0
        self.head_pitch_offset = 0.0
        self.head_roll_offset = 0.0
        self.eye_left_offset = 0.0
        self.eye_right_offset = 0.0
        self.mouth_open_offset = 0.0
        self.mouth_wide_offset = 0.0
        self.is_calibrated = False

    def reset(self):
        """Reset calibration to default values."""
        self.head_yaw_offset = 0.0
        self.head_pitch_offset = 0.0
        self.head_roll_offset = 0.0
        self.eye_left_offset = 0.0
        self.eye_right_offset = 0.0
        self.mouth_open_offset = 0.0
        self.mouth_wide_offset = 0.0
        self.is_calibrated = False

class FaceCalibrator:
    """
    Class to handle face calibration process.
    """
    def __init__(self, calibration_data=None):
        self.calibration_data = calibration_data or CalibrationData()
        self.calibration_samples = []
        self.is_calibrating = False
        self.required_samples = 30  # Number of samples to average during calibration
        self.current_sample_count = 0

    def start_calibration(self):
        """
        Start the calibration process.
        """
        self.is_calibrating = True
        self.calibration_samples = []
        self.current_sample_count = 0
        logging.info("Calibration started. Please look straight ahead with a neutral expression.")

    def collect_sample(self, tracking_data: FaceTrackingData):
        """
        Collect a sample for calibration if in calibration mode.
        
        Args:
            tracking_data: Current tracking data
        """
        if not self.is_calibrating or not tracking_data.face_detected:
            return False

        self.calibration_samples.append(tracking_data)
        self.current_sample_count += 1

        logging.debug(f"Calibration sample {self.current_sample_count}/{self.required_samples}")

        # Check if we have enough samples to complete calibration
        if self.current_sample_count >= self.required_samples:
            self.finish_calibration()
            return True

        return False

    def finish_calibration(self):
        """
        Finish the calibration process and compute average values.
        """
        if not self.calibration_samples:
            logging.warning("No samples collected during calibration")
            self.is_calibrating = False
            return

        # Calculate averages for each parameter
        avg_head_yaw = np.mean([sample.head_yaw for sample in self.calibration_samples])
        avg_head_pitch = np.mean([sample.head_pitch for sample in self.calibration_samples])
        avg_head_roll = np.mean([sample.head_roll for sample in self.calibration_samples])
        avg_eye_left = np.mean([sample.eye_left for sample in self.calibration_samples])
        avg_eye_right = np.mean([sample.eye_right for sample in self.calibration_samples])
        avg_mouth_open = np.mean([sample.mouth_open for sample in self.calibration_samples])
        avg_mouth_wide = np.mean([sample.mouth_wide for sample in self.calibration_samples])

        # Set calibration offsets (negative values to center the range)
        self.calibration_data.head_yaw_offset = avg_head_yaw
        self.calibration_data.head_pitch_offset = avg_head_pitch
        self.calibration_data.head_roll_offset = avg_head_roll
        self.calibration_data.eye_left_offset = avg_eye_left
        self.calibration_data.eye_right_offset = avg_eye_right
        self.calibration_data.mouth_open_offset = avg_mouth_open
        self.calibration_data.mouth_wide_offset = avg_mouth_wide
        self.calibration_data.is_calibrated = True

        # Clear samples
        self.calibration_samples = []
        self.is_calibrating = False

        logging.info("Calibration completed successfully")
        logging.info(f"Yaw offset: {self.calibration_data.head_yaw_offset:.3f}")
        logging.info(f"Pitch offset: {self.calibration_data.head_pitch_offset:.3f}")
        logging.info(f"Roll offset: {self.calibration_data.head_roll_offset:.3f}")
        logging.info(f"Eye left offset: {self.calibration_data.eye_left_offset:.3f}")
        logging.info(f"Eye right offset: {self.calibration_data.eye_right_offset:.3f}")
        logging.info(f"Mouth open offset: {self.calibration_data.mouth_open_offset:.3f}")
        logging.info(f"Mouth wide offset: {self.calibration_data.mouth_wide_offset:.3f}")

    def apply_calibration(self, tracking_data: FaceTrackingData) -> FaceTrackingData:
        """
        Apply calibration offsets to raw tracking data.
        
        Args:
            tracking_data: Raw tracking data
            
        Returns:
            Calibrated tracking data
        """
        if not self.calibration_data.is_calibrated:
            # If not calibrated, return original data without changes
            return tracking_data

        # Apply offsets to each parameter
        calibrated_data = FaceTrackingData(
            head_yaw=tracking_data.head_yaw - self.calibration_data.head_yaw_offset,
            head_pitch=tracking_data.head_pitch - self.calibration_data.head_pitch_offset,
            head_roll=tracking_data.head_roll - self.calibration_data.head_roll_offset,
            eye_left=max(0.0, min(1.0, tracking_data.eye_left - self.calibration_data.eye_left_offset)),
            eye_right=max(0.0, min(1.0, tracking_data.eye_right - self.calibration_data.eye_right_offset)),
            mouth_open=max(0.0, min(1.0, tracking_data.mouth_open - self.calibration_data.mouth_open_offset)),
            mouth_wide=max(0.0, min(1.0, tracking_data.mouth_wide - self.calibration_data.mouth_wide_offset)),
            face_detected=tracking_data.face_detected
        )

        # Apply additional adjustments to ensure proper range after calibration
        calibrated_data.head_yaw = max(-1.0, min(1.0, calibrated_data.head_yaw))
        calibrated_data.head_pitch = max(-1.0, min(1.0, calibrated_data.head_pitch))
        calibrated_data.head_roll = max(-1.0, min(1.0, calibrated_data.head_roll))

        return calibrated_data

    def is_calibration_complete(self) -> bool:
        """
        Check if calibration is complete.
        
        Returns:
            True if calibration is complete, False otherwise
        """
        return self.calibration_data.is_calibrated

    def get_calibration_status(self) -> str:
        """
        Get the current calibration status message.
        
        Returns:
            Status message string
        """
        if self.is_calibrating:
            progress = min(100, (self.current_sample_count / self.required_samples) * 100)
            return f"Calibrating... {progress:.0f}%"
        elif self.calibration_data.is_calibrated:
            return "Calibrated"
        else:
            return "Not calibrated"

    def reset_calibration(self):
        """
        Reset calibration to initial state.
        """
        self.calibration_data.reset()
        self.calibration_samples = []
        self.is_calibrating = False
        self.current_sample_count = 0
        logging.info("Calibration reset")


if __name__ == "__main__":
    # Test the calibration module
    from .face_tracking import FaceTrackingData

    print("Testing Face Calibration Module...")

    # Create test data with offsets to simulate neutral position
    test_data = [
        FaceTrackingData(head_yaw=0.1, head_pitch=0.05, eye_left=0.1, eye_right=0.1, mouth_open=0.05, mouth_wide=0.1),
        FaceTrackingData(head_yaw=0.08, head_pitch=0.03, eye_left=0.08, eye_right=0.09, mouth_open=0.04, mouth_wide=0.09),
        FaceTrackingData(head_yaw=0.12, head_pitch=0.06, eye_left=0.09, eye_right=0.11, mouth_open=0.06, mouth_wide=0.11),
    ]

    calibrator = FaceCalibrator()

    # Test calibration process
    print("Starting calibration...")
    calibrator.start_calibration()

    # Simulate calibration process
    for i, data in enumerate(test_data):
        is_finished = False
        # Simulate multiple samples of the same data to complete calibration
        for j in range(10):  # Add 10 samples of each data point to reach required samples
            is_finished = calibrator.collect_sample(data)
            if is_finished:
                break
        if is_finished:
            break

    print(f"Calibration finished: {calibrator.is_calibration_complete()}")
    print(f"Calibration status: {calibrator.get_calibration_status()}")

    # Test calibration application
    raw_data = FaceTrackingData(head_yaw=0.5, head_pitch=0.3, eye_left=0.7, eye_right=0.6, mouth_open=0.4, mouth_wide=0.3)
    calibrated_data = calibrator.apply_calibration(raw_data)

    print(f"Raw data:     Yaw={raw_data.head_yaw:.3f}, Pitch={raw_data.head_pitch:.3f}")
    print(f"Calibrated:   Yaw={calibrated_data.head_yaw:.3f}, Pitch={calibrated_data.head_pitch:.3f}")