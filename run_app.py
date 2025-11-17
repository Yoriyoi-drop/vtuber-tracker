#!/usr/bin/env python3
"""
Entry point for VTuber face tracking system.
This file allows running the application from the project root directory.
"""
import sys
import os
import argparse
import logging

# Add the project root to the path so modules can be imported properly
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import modules after adding project root to path
from gui.main_gui import main as gui_main
from tracker.camera import CameraCapture
from tracker.face_tracking import FaceTracker, FaceTrackingData
from tracker.smoothing import DataSmoother
from tracker.landmarks_to_params import LandmarksToParameters
from tracker.calibration import FaceCalibrator, CalibrationData
from tracker.precision_mode import PrecisionMode
from sender.vmc_sender import VMCSender
from sender.vts_sender import VTSSender


class VTuberTrackerApp:
    def __init__(self, stream_url=None):
        self.camera = None
        self.face_tracker = None
        self.smoother = None
        self.mapper = None
        self.calibrator = None
        self.precision_mode = None
        self.vmc_sender = None
        self.vts_sender = None
        self.is_running = False
        self.stream_url = stream_url  # URL untuk kamera Android/IP

        # Load configuration
        self.load_config()

        # Setup logging
        self.setup_logging()

    def load_config(self):
        """Load configuration from config.json."""
        import json
        try:
            with open("config/config.json", "r") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            # Default configuration
            self.config = {
                "camera": {
                    "default_camera_index": 0,
                    "frame_width": 640,
                    "frame_height": 480
                },
                "tracking": {
                    "max_faces": 1,
                    "min_detection_confidence": 0.5,
                    "min_tracking_confidence": 0.5
                },
                "smoothing": {
                    "alpha": 0.2,
                    "enabled": True
                },
                "calibration": {
                    "required_samples": 30,
                    "head_yaw_multiplier": 1.0,
                    "head_pitch_multiplier": 1.0,
                    "head_roll_multiplier": 1.0,
                    "eye_left_multiplier": 1.0,
                    "eye_right_multiplier": 1.0,
                    "mouth_open_multiplier": 1.0,
                    "mouth_wide_multiplier": 1.0,
                    "head_yaw_deadzone": 0.05,
                    "head_pitch_deadzone": 0.05,
                    "head_roll_deadzone": 0.05,
                    "eye_left_deadzone": 0.05,
                    "eye_right_deadzone": 0.05,
                    "mouth_open_deadzone": 0.05,
                    "mouth_wide_deadzone": 0.05
                },
                "precision": {
                    "enabled": False,
                    "sensitivity_multiplier": 1.5,
                    "noise_reduction_enabled": True,
                    "noise_threshold": 0.01,
                    "eye_blink_precision": True,
                    "mouth_precision": True,
                    "head_rotation_precision": True
                },
                "vmc": {
                    "host": "127.0.0.1",
                    "port": 39539,
                    "enabled": True
                },
                "vts": {
                    "host": "127.0.0.1",
                    "port": 8001,
                    "enabled": False
                },
                "gui": {
                    "window_width": 800,
                    "window_height": 600
                }
            }
            logging.info("Using default configuration")

    def setup_logging(self):
        """Setup logging configuration."""
        log_level = logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('vtuber_tracker.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def initialize_components(self):
        """Initialize all tracking components."""
        try:
            # Initialize camera - support both local and IP stream
            if self.stream_url:
                # Use IP stream (Android camera)
                self.camera = CameraCapture(
                    camera_index=self.config['camera']['default_camera_index'],
                    frame_width=self.config['camera']['frame_width'],
                    frame_height=self.config['camera']['frame_height'],
                    stream_url=self.stream_url
                )
            else:
                # Use local camera
                self.camera = CameraCapture(
                    camera_index=self.config['camera']['default_camera_index'],
                    frame_width=self.config['camera']['frame_width'],
                    frame_height=self.config['camera']['frame_height']
                )

            # Initialize face tracker
            self.face_tracker = FaceTracker(
                max_num_faces=self.config['tracking']['max_faces'],
                min_detection_confidence=self.config['tracking']['min_detection_confidence'],
                min_tracking_confidence=self.config['tracking']['min_tracking_confidence']
            )

            # Initialize smoother
            self.smoother = DataSmoother(
                alpha=self.config['smoothing']['alpha'],
                enabled=self.config['smoothing']['enabled']
            )

            # Initialize parameter mapper
            self.mapper = LandmarksToParameters()
            
            # Set mapper parameters from config
            self.mapper.update_sensitivity(
                head_yaw_multiplier=self.config['calibration']['head_yaw_multiplier'],
                head_pitch_multiplier=self.config['calibration']['head_pitch_multiplier'],
                head_roll_multiplier=self.config['calibration']['head_roll_multiplier'],
                eye_left_multiplier=self.config['calibration']['eye_left_multiplier'],
                eye_right_multiplier=self.config['calibration']['eye_right_multiplier'],
                mouth_open_multiplier=self.config['calibration']['mouth_open_multiplier'],
                mouth_wide_multiplier=self.config['calibration']['mouth_wide_multiplier']
            )
            
            self.mapper.update_deadzones(
                head_yaw_deadzone=self.config['calibration']['head_yaw_deadzone'],
                head_pitch_deadzone=self.config['calibration']['head_pitch_deadzone'],
                head_roll_deadzone=self.config['calibration']['head_roll_deadzone'],
                eye_left_deadzone=self.config['calibration']['eye_left_deadzone'],
                eye_right_deadzone=self.config['calibration']['eye_right_deadzone'],
                mouth_open_deadzone=self.config['calibration']['mouth_open_deadzone'],
                mouth_wide_deadzone=self.config['calibration']['mouth_wide_deadzone']
            )

            # Initialize calibrator
            calibration_data = CalibrationData()
            self.calibrator = FaceCalibrator(calibration_data)

            # Initialize precision mode
            self.precision_mode = PrecisionMode()
            self.precision_mode.set_precision_params(
                sensitivity_multiplier=self.config['precision']['sensitivity_multiplier'],
                noise_reduction_enabled=self.config['precision']['noise_reduction_enabled'],
                noise_threshold=self.config['precision']['noise_threshold'],
                eye_blink_precision=self.config['precision']['eye_blink_precision'],
                mouth_precision=self.config['precision']['mouth_precision'],
                head_rotation_precision=self.config['precision']['head_rotation_precision']
            )
            
            # Enable precision mode if configured
            if self.config['precision']['enabled']:
                self.precision_mode.enable_precision_mode(self.config['precision']['sensitivity_multiplier'])

            # Initialize senders
            self.vmc_sender = VMCSender(
                host=self.config['vmc']['host'],
                port=self.config['vmc']['port'],
                enabled=self.config['vmc']['enabled']
            )

            self.vts_sender = VTSSender(
                host=self.config['vts']['host'],
                port=self.config['vts']['port'],
                enabled=self.config['vts']['enabled']
            )

            self.logger.info("All components initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error initializing components: {e}")
            return False

    def run_tracking_loop(self):
        """Run the main tracking loop (for command-line mode)."""
        if not self.initialize_components():
            return False

        self.is_running = True
        self.logger.info("Starting tracking loop...")

        try:
            while self.is_running:
                # Get frame from camera
                frame = self.camera.get_frame()
                if frame is None:
                    continue

                # Process face tracking
                raw_data = self.face_tracker.process_frame(frame)

                # Apply calibration if active
                if self.calibrator.is_calibrating:
                    # Collect sample for calibration
                    is_calibrated = self.calibrator.collect_sample(raw_data)
                    if is_calibrated:
                        self.logger.info("Calibration completed")
                    # Use raw data during calibration
                    calibrated_data = raw_data
                else:
                    # Apply calibration to tracking data if calibration exists
                    calibrated_data = self.calibrator.apply_calibration(raw_data)

                # Apply precision mode enhancement if enabled
                enhanced_data = self.precision_mode.enhance_tracking_data(calibrated_data)

                # Apply smoothing
                smoothed_data = self.smoother.smooth_data(enhanced_data)

                # Map to parameters
                all_params = self.mapper.process_tracking_data(smoothed_data, "both")

                # Send to VMC if enabled
                if self.config['vmc']['enabled'] and self.vmc_sender.is_connected:
                    self.vmc_sender.send_tracking_data(all_params.get("vmc", {}))

                # Send to VTS if enabled
                if self.config['vts']['enabled'] and self.vts_sender.is_connected:
                    self.vts_sender.send_tracking_data(all_params.get("vts", {}))

                # Print tracking data if in verbose mode
                if hasattr(self, 'verbose') and self.verbose:
                    print(f"Yaw: {smoothed_data.head_yaw:.2f}, "
                          f"Pitch: {smoothed_data.head_pitch:.2f}, "
                          f"Roll: {smoothed_data.head_roll:.2f}, "
                          f"Left Eye: {smoothed_data.eye_left:.2f}, "
                          f"Right Eye: {smoothed_data.eye_right:.2f}, "
                          f"Mouth Open: {smoothed_data.mouth_open:.2f}, "
                          f"Mouth Wide: {smoothed_data.mouth_wide:.2f}, "
                          f"Calibrated: {self.calibrator.calibration_data.is_calibrated}, "
                          f"Precision: {self.precision_mode.enabled}")

                # Small delay to control frame rate
                import time
                time.sleep(1/30)  # ~30 FPS

        except KeyboardInterrupt:
            self.logger.info("Tracking interrupted by user")
        except Exception as e:
            self.logger.error(f"Error in tracking loop: {e}")
        finally:
            self.cleanup()
            return True

    def run_gui(self):
        """Run the GUI application."""
        try:
            # Use the existing GUI main function
            return gui_main()
        except Exception as e:
            self.logger.error(f"Error running GUI: {e}")
            return False

    def cleanup(self):
        """Clean up resources."""
        if self.camera:
            self.camera.release()
            self.camera = None

        if self.face_tracker:
            self.face_tracker.release()
            self.face_tracker = None

        if self.vmc_sender:
            self.vmc_sender.disconnect()
            self.vmc_sender = None

        if self.vts_sender:
            self.vts_sender.disconnect()
            self.vts_sender = None

        # Clean up additional components
        self.calibrator = None
        self.precision_mode = None

        self.is_running = False
        self.logger.info("Cleanup completed")


def main():
    parser = argparse.ArgumentParser(description='VTuber Face Tracking System')
    parser.add_argument('--mode', choices=['gui', 'cli'], default='gui',
                        help='Run mode: gui (default) or cli (command-line)')
    parser.add_argument('--camera', type=int, default=None,
                        help='Camera index to use')
    parser.add_argument('--stream-url', type=str, default=None,
                        help='IP stream URL for Android/iPhone camera (e.g., http://192.168.1.100:8080/video)')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose output in CLI mode')

    args = parser.parse_args()

    # Initialize app with stream URL if provided
    app = VTuberTrackerApp(stream_url=args.stream_url)

    # Override config with command line args if provided
    if args.camera is not None:
        app.config['camera']['default_camera_index'] = args.camera

    if args.mode == 'cli':
        app.verbose = args.verbose
        success = app.run_tracking_loop()
    else:
        success = app.run_gui()

    # Cleanup is handled in the respective run methods
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()