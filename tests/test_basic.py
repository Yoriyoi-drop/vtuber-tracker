"""
Basic tests for VTuber Tracker library
"""
import pytest
import sys
import os

# Add the project root to the path so modules can be imported properly
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_imports():
    """Test that all main modules can be imported without error."""
    try:
        from vtuber_tracker_lib import VTuberTracker, VTuberConfig
        from tracker.face_tracking import FaceTracker
        from tracker.calibration import FaceCalibrator
        from tracker.smoothing import DataSmoother
        from tracker.landmarks_to_params import LandmarksToParameters
        from tracker.precision_mode import PrecisionMode
        from sender.vmc_sender import VMCSender
        from sender.vts_sender import VTSSender
        from tracker.camera import CameraCapture
        assert True  # If all imports work, test passes
    except ImportError as e:
        pytest.fail(f"Failed to import module: {e}")

def test_config_creation():
    """Test that VTuberConfig can be created with default parameters."""
    from vtuber_tracker_lib import VTuberConfig
    
    config = VTuberConfig()
    
    # Test that default values are reasonable
    assert config.camera_index == 0
    assert config.frame_width == 640
    assert config.frame_height == 480
    assert 0.0 <= config.smoothing_alpha <= 1.0
    assert isinstance(config.enable_virtual_camera, bool)
    assert isinstance(config.enable_vmc_output, bool)

def test_tracker_creation():
    """Test that VTuberTracker can be created with a config."""
    from vtuber_tracker_lib import VTuberTracker, VTuberConfig
    
    config = VTuberConfig()
    tracker = VTuberTracker(config)
    
    # Test that the tracker object has necessary attributes
    assert hasattr(tracker, 'config')
    assert hasattr(tracker, 'camera')
    assert hasattr(tracker, 'face_tracker')
    assert hasattr(tracker, 'smoother')
    assert hasattr(tracker, 'mapper')
    assert hasattr(tracker, 'calibrator')
    assert hasattr(tracker, 'precision_mode')