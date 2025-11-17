"""
VTuber Tracker Library - Simple Python Library for Face Tracking

Installation:
pip install opencv-python mediapipe pyqt5 python-osc websocket-client requests numpy pyfakewebcam

Usage:
from vtuber_tracker_lib import VTuberTracker

# Initialize tracker
tracker = VTuberTracker()

# Start tracking
tracker.start()

# Stop tracking
tracker.stop()
"""

import cv2
import mediapipe as mp
import numpy as np
import logging
from dataclasses import dataclass
from typing import Optional, Tuple
import time
import threading

# Import modules we created
from tracker.face_tracking import FaceTracker, FaceTrackingData
from tracker.smoothing import DataSmoother
from tracker.landmarks_to_params import LandmarksToParameters
from tracker.calibration import FaceCalibrator, CalibrationData
from tracker.precision_mode import PrecisionMode
from tracker.virtual_camera import create_virtual_camera
from sender.vmc_sender import VMCSender


@dataclass
class VTuberConfig:
    """Configuration for VTuber tracker"""
    camera_index: int = 0
    frame_width: int = 640
    frame_height: int = 480
    smoothing_alpha: float = 0.2
    enable_smoothing: bool = True
    enable_virtual_camera: bool = False
    virtual_camera_width: int = 640
    virtual_camera_height: int = 480
    virtual_camera_fps: int = 30
    vmc_host: str = "127.0.0.1"
    vmc_port: int = 39539
    enable_vmc_output: bool = True
    stream_url: Optional[str] = None  # URL untuk stream kamera IP/Android


class VTuberTracker:
    """
    Simple VTuber face tracking library that can be used by your friend
    """
    
    def __init__(self, config: VTuberConfig = None):
        self.config = config or VTuberConfig()
        self.is_running = False
        self.tracking_thread = None
        
        # Initialize components
        self.camera = None
        self.face_tracker = None
        self.smoother = None
        self.mapper = None
        self.calibrator = None
        self.precision_mode = None
        self.virtual_camera = None
        self.vmc_sender = None
        
        self.setup_logging()
        self.initialize_components()

    def _get_available_cameras(self, max_cameras=10):
        """Deteksi kamera yang tersedia."""
        import cv2
        available_cameras = []

        for i in range(max_cameras):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:  # Pastikan bisa membaca frame, bukan hanya membuka perangkat
                    available_cameras.append(i)
                cap.release()
            else:
                break  # Jika tidak bisa buka, berhenti di sini

        return available_cameras

    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def initialize_components(self):
        """Initialize all tracking components."""
        try:
            # Initialize camera with detection and fallback
            from tracker.camera import CameraCapture

            # Check if using IP stream
            if self.config.stream_url:
                # Use IP stream instead of local camera
                self.camera = CameraCapture(
                    camera_index=self.config.camera_index,
                    frame_width=self.config.frame_width,
                    frame_height=self.config.frame_height,
                    stream_url=self.config.stream_url
                )
            else:
                # First, try to detect available cameras
                available_cameras = self._get_available_cameras()
                if not available_cameras:
                    raise RuntimeError("Tidak ada kamera yang terdeteksi. Pastikan kamera terhubung dan tidak digunakan aplikasi lain.")

                # Check if the configured camera index is available
                if self.config.camera_index not in available_cameras:
                    print(f"Kamera indeks {self.config.camera_index} tidak tersedia.")
                    print(f"Kamera yang tersedia: {available_cameras}")
                    print(f"Menggunakan kamera pertama: {available_cameras[0]}")
                    actual_camera_index = available_cameras[0]
                else:
                    actual_camera_index = self.config.camera_index

                # Initialize with actual available camera
                self.camera = CameraCapture(
                    camera_index=actual_camera_index,
                    frame_width=self.config.frame_width,
                    frame_height=self.config.frame_height
                )
            
            # Initialize face tracker
            self.face_tracker = FaceTracker()
            
            # Initialize smoother
            self.smoother = DataSmoother(
                alpha=self.config.smoothing_alpha,
                enabled=self.config.enable_smoothing
            )
            
            # Initialize parameter mapper
            self.mapper = LandmarksToParameters()
            
            # Initialize calibrator
            calibration_data = CalibrationData()
            self.calibrator = FaceCalibrator(calibration_data)
            
            # Initialize precision mode
            self.precision_mode = PrecisionMode()
            
            # Initialize virtual camera if enabled
            if self.config.enable_virtual_camera:
                self.virtual_camera = create_virtual_camera(
                    width=self.config.virtual_camera_width,
                    height=self.config.virtual_camera_height,
                    fps=self.config.virtual_camera_fps
                )
                if self.virtual_camera:
                    self.virtual_camera.enable_output(True)
            
            # Initialize VMC sender
            if self.config.enable_vmc_output:
                self.vmc_sender = VMCSender(
                    host=self.config.vmc_host,
                    port=self.config.vmc_port,
                    enabled=True
                )
            
            self.logger.info("All VTuber tracker components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing components: {e}")
            raise
    
    def start(self):
        """Start the tracking process."""
        if self.is_running:
            self.logger.warning("Tracker is already running")
            return
        
        self.is_running = True
        self.tracking_thread = threading.Thread(target=self._tracking_loop, daemon=True)
        self.tracking_thread.start()
        self.logger.info("VTuber tracker started")
    
    def stop(self):
        """Stop the tracking process."""
        self.is_running = False
        if self.tracking_thread:
            self.tracking_thread.join(timeout=2.0)
        self.cleanup()
        self.logger.info("VTuber tracker stopped")
    
    def _tracking_loop(self):
        """Main tracking loop running in separate thread."""
        self.logger.info("Tracking loop started")
        
        while self.is_running:
            try:
                # Get frame from camera
                frame = self.camera.get_frame()
                if frame is None:
                    time.sleep(0.01)  # Small delay if no frame available
                    continue
                
                # Process face tracking
                raw_data = self.face_tracker.process_frame(frame)
                
                # Apply calibration if active
                if self.calibrator.is_calibrating:
                    is_calibrated = self.calibrator.collect_sample(raw_data)
                    if is_calibrated:
                        self.logger.info("Calibration completed")
                    calibrated_data = raw_data
                else:
                    calibrated_data = self.calibrator.apply_calibration(raw_data)
                
                # Apply precision mode enhancement if enabled
                enhanced_data = self.precision_mode.enhance_tracking_data(calibrated_data)
                
                # Apply smoothing
                smoothed_data = self.smoother.smooth_data(enhanced_data)
                
                # Map to parameters
                all_params = self.mapper.process_tracking_data(smoothed_data, "vmc")
                
                # Send to VMC if enabled
                if self.vmc_sender and self.vmc_sender.is_connected:
                    self.vmc_sender.send_tracking_data(all_params.get("vmc", {}))
                
                # Send frame to virtual camera if enabled
                if self.virtual_camera:
                    frame_with_landmarks = self.face_tracker.draw_landmarks(frame.copy(), 
                                                                           self.face_tracker.get_landmarks(frame))
                    self.virtual_camera.send_frame(frame_with_landmarks)
                
                # Small delay to control frame rate (~30 FPS)
                time.sleep(1/30)
                
            except Exception as e:
                self.logger.error(f"Error in tracking loop: {e}")
                time.sleep(0.1)  # Brief pause before continuing
        
        self.logger.info("Tracking loop ended")
    
    def start_calibration(self):
        """Start the calibration process."""
        if self.calibrator:
            self.calibrator.start_calibration()
            self.logger.info("Calibration started")
    
    def is_calibrated(self) -> bool:
        """Check if calibration is complete."""
        return self.calibrator.calibration_data.is_calibrated if self.calibrator else False
    
    def enable_precision_mode(self, enabled: bool = True, multiplier: float = 1.5):
        """Enable or disable precision mode."""
        if self.precision_mode:
            if enabled:
                self.precision_mode.enable_precision_mode(multiplier)
            else:
                self.precision_mode.disable_precision_mode()
    
    def cleanup(self):
        """Clean up all resources."""
        if self.camera:
            self.camera.release()
        
        if self.vmc_sender:
            self.vmc_sender.disconnect()
        
        if self.virtual_camera:
            self.virtual_camera.release()
        
        # Clean up other components
        self.camera = None
        self.face_tracker = None
        self.smoother = None
        self.mapper = None
        self.calibrator = None
        self.precision_mode = None
        self.virtual_camera = None
        self.vmc_sender = None
        
        self.logger.info("VTuber tracker cleaned up")


def main():
    """Example usage of the VTuber tracker library."""
    print("VTuber Tracker Library Example")
    print("=" * 40)
    
    # Create configuration
    config = VTuberConfig(
        enable_virtual_camera=False,  # Disable for this example
        enable_vmc_output=True
    )
    
    # Create and start tracker
    tracker = VTuberTracker(config)
    tracker.start()
    
    print("Tracker started. Press Ctrl+C to stop.")
    
    try:
        # Keep running for 30 seconds as example
        import signal
        import sys
        
        def signal_handler(sig, frame):
            print('\nStopping tracker...')
            tracker.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        time.sleep(30)  # Run for 30 seconds
        
    except KeyboardInterrupt:
        print("\nStopping tracker...")
    
    tracker.stop()
    print("Tracker stopped.")


if __name__ == "__main__":
    main()