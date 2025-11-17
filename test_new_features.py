#!/usr/bin/env python3
"""
Test script to verify the new features in VTuber Tracker.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tracker.calibration import FaceCalibrator, CalibrationData
from tracker.precision_mode import PrecisionMode
from tracker.landmarks_to_params import LandmarksToParameters
from tracker.face_tracking import FaceTrackingData

def test_calibration():
    """Test calibration functionality."""
    print("Testing Calibration...")
    
    # Create calibrator
    calibrator = FaceCalibrator()
    
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
    
    print(f"Original data: Yaw={test_data.head_yaw}, Pitch={test_data.head_pitch}")
    
    # Test without calibration
    result1 = calibrator.apply_calibration(test_data)
    print(f"Without calibration: Yaw={result1.head_yaw}, Pitch={result1.head_pitch}")
    
    # Perform a simple calibration
    calibrator.start_calibration()
    
    # Add a sample to calibration
    for i in range(30):  # Collect required samples
        is_finished = calibrator.collect_sample(test_data)
        if is_finished:
            break
            
    print(f"Calibration completed: {calibrator.calibration_data.is_calibrated}")
    print(f"Calibration offsets - Yaw: {calibrator.calibration_data.head_yaw_offset:.3f}, "
          f"Pitch: {calibrator.calibration_data.head_pitch_offset:.3f}")
    
    # Test with calibration applied
    result2 = calibrator.apply_calibration(test_data)
    print(f"With calibration: Yaw={result2.head_yaw:.3f}, Pitch={result2.head_pitch:.3f}")
    
    print("Calibration test completed.\n")


def test_precision_mode():
    """Test precision mode functionality."""
    print("Testing Precision Mode...")
    
    # Create precision mode
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
    
    print(f"Original data: Yaw={test_data.head_yaw}, Eye Left={test_data.eye_left}")
    
    # Test without precision mode
    result1 = precision.enhance_tracking_data(test_data)
    print(f"Without precision: Yaw={result1.head_yaw}, Eye Left={result1.eye_left}")
    
    # Enable precision mode
    precision.enable_precision_mode(multiplier=2.0)
    result2 = precision.enhance_tracking_data(test_data)
    print(f"With precision (x2.0): Yaw={result2.head_yaw:.3f}, Eye Left={result2.eye_left:.3f}")
    
    print("Precision mode test completed.\n")


def test_advanced_sensitivity():
    """Test advanced sensitivity controls."""
    print("Testing Advanced Sensitivity...")
    
    # Create mapper
    mapper = LandmarksToParameters()
    
    # Create test data
    test_data = FaceTrackingData(
        head_yaw=0.3,
        head_pitch=0.2,
        head_roll=0.1,
        eye_left=0.4,
        eye_right=0.5,
        mouth_open=0.6,
        mouth_wide=0.3,
        face_detected=True
    )
    
    print(f"Original sensitivity: Head Yaw={test_data.head_yaw}, Eye Left={test_data.eye_left}")
    
    # Test with default parameters
    params1 = mapper.map_to_vmc_params(test_data)
    print(f"With default sensitivity: VMC Head Yaw={params1['head_yaw']:.3f}, Blink_L={params1['Blink_L']:.3f}")
    
    # Update sensitivity
    mapper.update_sensitivity(
        head_yaw_multiplier=1.5,
        eye_left_multiplier=0.7
    )
    
    # Test with updated sensitivity
    params2 = mapper.map_to_vmc_params(test_data)
    print(f"With updated sensitivity: VMC Head Yaw={params2['head_yaw']:.3f}, Blink_L={params2['Blink_L']:.3f}")
    
    print("Advanced sensitivity test completed.\n")


def test_deadzone():
    """Test deadzone functionality."""
    print("Testing Deadzone...")
    
    # Create mapper
    mapper = LandmarksToParameters()
    
    # Create test data with small values (should be affected by deadzone)
    test_data = FaceTrackingData(
        head_yaw=0.02,  # Below default deadzone of 0.05
        head_pitch=0.08,  # Above default deadzone
        eye_left=0.03,  # Below default deadzone
        eye_right=0.06,  # Above default deadzone
        mouth_open=0.04,  # Below default deadzone
        mouth_wide=0.07,  # Above default deadzone
        face_detected=True
    )
    
    print(f"Original data: Yaw={test_data.head_yaw}, Pitch={test_data.head_pitch}")
    
    # Test with default parameters (with deadzone)
    params1 = mapper.map_to_vmc_params(test_data)
    print(f"With deadzone: VMC Head Yaw={params1['head_yaw']:.3f}, Pitch={params1['head_pitch']:.3f}")
    
    # Update deadzone to 0 (no deadzone)
    mapper.update_deadzones(
        head_yaw_deadzone=0.0,
        head_pitch_deadzone=0.0,
        eye_left_deadzone=0.0,
        eye_right_deadzone=0.0,
        mouth_open_deadzone=0.0,
        mouth_wide_deadzone=0.0
    )
    
    # Test with no deadzone
    params2 = mapper.map_to_vmc_params(test_data)
    print(f"Without deadzone: VMC Head Yaw={params2['head_yaw']:.3f}, Pitch={params2['head_pitch']:.3f}")
    
    print("Deadzone test completed.\n")


if __name__ == "__main__":
    print("VTuber Tracker - New Features Test Suite")
    print("=" * 50)
    
    test_calibration()
    test_precision_mode()
    test_advanced_sensitivity()
    test_deadzone()
    
    print("All tests completed!")