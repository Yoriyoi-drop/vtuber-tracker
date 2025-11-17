"""
GUI module for VTuber face tracking system.
Provides a PyQt5-based interface for camera selection and tracking control.
"""
import sys
import json
import logging
import os
# Add the project root to the path so modules can be imported properly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QComboBox, QLabel,
                             QCheckBox, QGroupBox, QGridLayout, QMessageBox,
                             QTabWidget, QScrollArea, QFrame, QSlider)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
import cv2
from tracker.camera import CameraCapture
from tracker.face_tracking import FaceTracker
from tracker.smoothing import DataSmoother
from tracker.landmarks_to_params import LandmarksToParameters
from tracker.calibration import FaceCalibrator, CalibrationData
from tracker.precision_mode import PrecisionMode
from tracker.virtual_camera import create_virtual_camera
from sender.vmc_sender import VMCSender
from sender.vts_sender import VTSSender

class TrackingWorker(QThread):
    """Worker thread for face tracking to prevent GUI freezing."""
    frame_processed = pyqtSignal(object)  # Emits processed frame
    tracking_data_ready = pyqtSignal(object)  # Emits tracking data

    def __init__(self, camera, face_tracker, smoother, mapper, calibrator, precision_mode, virtual_camera,
                 vmc_sender, vts_sender, vmc_enabled, vts_enabled):
        super().__init__()
        self.camera = camera
        self.face_tracker = face_tracker
        self.smoother = smoother
        self.mapper = mapper
        self.calibrator = calibrator
        self.precision_mode = precision_mode
        self.virtual_camera = virtual_camera
        self.vmc_sender = vmc_sender
        self.vts_sender = vts_sender
        self.vmc_enabled = vmc_enabled
        self.vts_enabled = vts_enabled
        self.running = False

    def run(self):
        """Main tracking loop."""
        self.running = True
        while self.running:
            frame = self.camera.get_frame()
            if frame is not None:
                # Process frame to get landmarks
                results = self.face_tracker.get_landmarks(frame)

                # Draw landmarks on frame
                frame_with_landmarks = self.face_tracker.draw_landmarks(frame.copy(), results)

                # Process face tracking
                raw_data = self.face_tracker.process_frame(frame)

                # Apply calibration if active
                if self.calibrator.is_calibrating:
                    # Collect sample for calibration
                    is_calibrated = self.calibrator.collect_sample(raw_data)
                    if is_calibrated:
                        logging.info("Calibration completed")
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
                if self.vmc_enabled and self.vmc_sender.is_connected:
                    self.vmc_sender.send_tracking_data(all_params.get("vmc", {}))

                # Send to VTS if enabled
                if self.vts_enabled and self.vts_sender.is_connected:
                    self.vts_sender.send_tracking_data(all_params.get("vts", {}))

                # Send frame to virtual camera if enabled
                if self.virtual_camera:
                    self.virtual_camera.send_frame(frame_with_landmarks)

                # Emit processed frame and tracking data
                self.frame_processed.emit(frame_with_landmarks)
                self.tracking_data_ready.emit(smoothed_data)

                # Small delay to control frame rate
                self.msleep(33)  # ~30 FPS
            else:
                self.msleep(100)  # Wait longer if no frame available

    def stop(self):
        """Stop the tracking loop."""
        self.running = False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VTuber Face Tracker")
        self.setGeometry(100, 100, 1000, 800)

        # Load config
        self.load_config()

        # Initialize components
        self.camera = None
        self.face_tracker = None
        self.smoother = None
        self.mapper = None
        self.calibrator = None
        self.precision_mode = None
        self.vmc_sender = None
        self.vts_sender = None
        self.tracking_worker = None

        # Create UI
        self.init_ui()

        # Initialize tracking components
        self.init_tracking()

        # Update camera list
        self.update_camera_list()
    
    def load_config(self):
        """Load configuration from config.json."""
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
    
    def init_ui(self):
        """Initialize the user interface."""
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tabs
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # Camera control tab
        camera_tab = self.create_camera_tab()
        tabs.addTab(camera_tab, "Camera")
        
        # Tracking control tab
        tracking_tab = self.create_tracking_tab()
        tabs.addTab(tracking_tab, "Tracking")
        
        # Output control tab
        output_tab = self.create_output_tab()
        tabs.addTab(output_tab, "Output")
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
    
    def create_camera_tab(self):
        """Create the camera control tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Camera selection group
        camera_group = QGroupBox("Camera Settings")
        camera_layout = QVBoxLayout(camera_group)
        
        # Camera selection
        camera_select_layout = QHBoxLayout()
        camera_select_layout.addWidget(QLabel("Camera:"))
        self.camera_combo = QComboBox()
        self.camera_combo.currentIndexChanged.connect(self.on_camera_changed)
        camera_select_layout.addWidget(self.camera_combo)
        
        self.refresh_camera_btn = QPushButton("Refresh Cameras")
        self.refresh_camera_btn.clicked.connect(self.update_camera_list)
        camera_select_layout.addWidget(self.refresh_camera_btn)
        
        camera_layout.addLayout(camera_select_layout)
        
        # Camera preview
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(640, 480)
        self.preview_label.setStyleSheet("border: 1px solid gray;")
        camera_layout.addWidget(self.preview_label)
        
        # Start/Stop buttons
        control_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Tracking")
        self.start_btn.clicked.connect(self.start_tracking)
        self.start_btn.setEnabled(False)
        
        self.stop_btn = QPushButton("Stop Tracking")
        self.stop_btn.clicked.connect(self.stop_tracking)
        self.stop_btn.setEnabled(False)
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        camera_layout.addLayout(control_layout)
        
        layout.addWidget(camera_group)
        
        return tab
    
    def create_tracking_tab(self):
        """Create the tracking control tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Smoothing settings
        smoothing_group = QGroupBox("Smoothing Settings")
        smoothing_layout = QGridLayout(smoothing_group)

        smoothing_layout.addWidget(QLabel("Smoothing Alpha:"), 0, 0)
        self.smoothing_alpha_label = QLabel(f"{self.config['smoothing']['alpha']:.2f}")
        smoothing_layout.addWidget(self.smoothing_alpha_label, 0, 1)

        self.smoothing_alpha_slider = QSlider(Qt.Horizontal)
        self.smoothing_alpha_slider.setRange(0, 100)
        self.smoothing_alpha_slider.setValue(int(self.config['smoothing']['alpha'] * 100))
        self.smoothing_alpha_slider.valueChanged.connect(self.on_smoothing_alpha_changed)
        smoothing_layout.addWidget(self.smoothing_alpha_slider, 0, 2)

        self.smoothing_toggle = QCheckBox("Enable Smoothing")
        self.smoothing_toggle.setChecked(self.config['smoothing']['enabled'])
        self.smoothing_toggle.stateChanged.connect(self.on_smoothing_toggle)
        smoothing_layout.addWidget(self.smoothing_toggle, 1, 0, 1, 3)

        layout.addWidget(smoothing_group)

        # Calibration settings
        calibration_group = QGroupBox("Calibration Settings")
        calibration_layout = QGridLayout(calibration_group)

        self.calibrate_btn = QPushButton("Start Calibration")
        self.calibrate_btn.clicked.connect(self.start_calibration)
        calibration_layout.addWidget(self.calibrate_btn, 0, 0)

        self.calibration_status_label = QLabel("Status: Not calibrated")
        calibration_layout.addWidget(self.calibration_status_label, 0, 1)

        self.reset_calibration_btn = QPushButton("Reset Calibration")
        self.reset_calibration_btn.clicked.connect(self.reset_calibration)
        calibration_layout.addWidget(self.reset_calibration_btn, 1, 0, 1, 2)

        layout.addWidget(calibration_group)

        # Advanced sensitivity settings
        advanced_sensitivity_group = QGroupBox("Advanced Sensitivity Settings")
        advanced_sensitivity_layout = QGridLayout(advanced_sensitivity_group)

        # Head rotation sensitivity (individual axes)
        advanced_sensitivity_layout.addWidget(QLabel("Head Yaw Sensitivity:"), 0, 0)
        self.head_yaw_sensitivity_slider = QSlider(Qt.Horizontal)
        self.head_yaw_sensitivity_slider.setRange(10, 300)
        self.head_yaw_sensitivity_slider.setValue(int(self.config['calibration']['head_yaw_multiplier'] * 100))  # Default 1.0 multiplier
        self.head_yaw_sensitivity_slider.valueChanged.connect(self.on_head_yaw_sensitivity_changed)
        advanced_sensitivity_layout.addWidget(self.head_yaw_sensitivity_slider, 0, 1)

        self.head_yaw_sensitivity_label = QLabel(f"{self.config['calibration']['head_yaw_multiplier']:.2f}")
        advanced_sensitivity_layout.addWidget(self.head_yaw_sensitivity_label, 0, 2)

        advanced_sensitivity_layout.addWidget(QLabel("Head Pitch Sensitivity:"), 1, 0)
        self.head_pitch_sensitivity_slider = QSlider(Qt.Horizontal)
        self.head_pitch_sensitivity_slider.setRange(10, 300)
        self.head_pitch_sensitivity_slider.setValue(int(self.config['calibration']['head_pitch_multiplier'] * 100))  # Default 1.0 multiplier
        self.head_pitch_sensitivity_slider.valueChanged.connect(self.on_head_pitch_sensitivity_changed)
        advanced_sensitivity_layout.addWidget(self.head_pitch_sensitivity_slider, 1, 1)

        self.head_pitch_sensitivity_label = QLabel(f"{self.config['calibration']['head_pitch_multiplier']:.2f}")
        advanced_sensitivity_layout.addWidget(self.head_pitch_sensitivity_label, 1, 2)

        advanced_sensitivity_layout.addWidget(QLabel("Head Roll Sensitivity:"), 2, 0)
        self.head_roll_sensitivity_slider = QSlider(Qt.Horizontal)
        self.head_roll_sensitivity_slider.setRange(10, 300)
        self.head_roll_sensitivity_slider.setValue(int(self.config['calibration']['head_roll_multiplier'] * 100))  # Default 1.0 multiplier
        self.head_roll_sensitivity_slider.valueChanged.connect(self.on_head_roll_sensitivity_changed)
        advanced_sensitivity_layout.addWidget(self.head_roll_sensitivity_slider, 2, 1)

        self.head_roll_sensitivity_label = QLabel(f"{self.config['calibration']['head_roll_multiplier']:.2f}")
        advanced_sensitivity_layout.addWidget(self.head_roll_sensitivity_label, 2, 2)

        # Eye sensitivity (individual eyes)
        advanced_sensitivity_layout.addWidget(QLabel("Eye Left Sensitivity:"), 3, 0)
        self.eye_left_sensitivity_slider = QSlider(Qt.Horizontal)
        self.eye_left_sensitivity_slider.setRange(10, 300)
        self.eye_left_sensitivity_slider.setValue(int(self.config['calibration']['eye_left_multiplier'] * 100))  # Default 1.0 multiplier
        self.eye_left_sensitivity_slider.valueChanged.connect(self.on_eye_left_sensitivity_changed)
        advanced_sensitivity_layout.addWidget(self.eye_left_sensitivity_slider, 3, 1)

        self.eye_left_sensitivity_label = QLabel(f"{self.config['calibration']['eye_left_multiplier']:.2f}")
        advanced_sensitivity_layout.addWidget(self.eye_left_sensitivity_label, 3, 2)

        advanced_sensitivity_layout.addWidget(QLabel("Eye Right Sensitivity:"), 4, 0)
        self.eye_right_sensitivity_slider = QSlider(Qt.Horizontal)
        self.eye_right_sensitivity_slider.setRange(10, 300)
        self.eye_right_sensitivity_slider.setValue(int(self.config['calibration']['eye_right_multiplier'] * 100))  # Default 1.0 multiplier
        self.eye_right_sensitivity_slider.valueChanged.connect(self.on_eye_right_sensitivity_changed)
        advanced_sensitivity_layout.addWidget(self.eye_right_sensitivity_slider, 4, 1)

        self.eye_right_sensitivity_label = QLabel(f"{self.config['calibration']['eye_right_multiplier']:.2f}")
        advanced_sensitivity_layout.addWidget(self.eye_right_sensitivity_label, 4, 2)

        # Mouth sensitivity
        advanced_sensitivity_layout.addWidget(QLabel("Mouth Open Sensitivity:"), 5, 0)
        self.mouth_open_sensitivity_slider = QSlider(Qt.Horizontal)
        self.mouth_open_sensitivity_slider.setRange(10, 300)
        self.mouth_open_sensitivity_slider.setValue(int(self.config['calibration']['mouth_open_multiplier'] * 100))  # Default 1.0 multiplier
        self.mouth_open_sensitivity_slider.valueChanged.connect(self.on_mouth_open_sensitivity_changed)
        advanced_sensitivity_layout.addWidget(self.mouth_open_sensitivity_slider, 5, 1)

        self.mouth_open_sensitivity_label = QLabel(f"{self.config['calibration']['mouth_open_multiplier']:.2f}")
        advanced_sensitivity_layout.addWidget(self.mouth_open_sensitivity_label, 5, 2)

        advanced_sensitivity_layout.addWidget(QLabel("Mouth Wide Sensitivity:"), 6, 0)
        self.mouth_wide_sensitivity_slider = QSlider(Qt.Horizontal)
        self.mouth_wide_sensitivity_slider.setRange(10, 300)
        self.mouth_wide_sensitivity_slider.setValue(int(self.config['calibration']['mouth_wide_multiplier'] * 100))  # Default 1.0 multiplier
        self.mouth_wide_sensitivity_slider.valueChanged.connect(self.on_mouth_wide_sensitivity_changed)
        advanced_sensitivity_layout.addWidget(self.mouth_wide_sensitivity_slider, 6, 1)

        self.mouth_wide_sensitivity_label = QLabel(f"{self.config['calibration']['mouth_wide_multiplier']:.2f}")
        advanced_sensitivity_layout.addWidget(self.mouth_wide_sensitivity_label, 6, 2)

        layout.addWidget(advanced_sensitivity_group)

        # Deadzone settings
        deadzone_group = QGroupBox("Deadzone Settings")
        deadzone_layout = QGridLayout(deadzone_group)

        # Head rotation deadzones
        deadzone_layout.addWidget(QLabel("Head Yaw Deadzone:"), 0, 0)
        self.head_yaw_deadzone_slider = QSlider(Qt.Horizontal)
        self.head_yaw_deadzone_slider.setRange(0, 200)  # 0 to 0.20
        self.head_yaw_deadzone_slider.setValue(int(self.config['calibration']['head_yaw_deadzone'] * 1000))  # Scale by 1000
        self.head_yaw_deadzone_slider.valueChanged.connect(self.on_head_yaw_deadzone_changed)
        deadzone_layout.addWidget(self.head_yaw_deadzone_slider, 0, 1)

        self.head_yaw_deadzone_label = QLabel(f"{self.config['calibration']['head_yaw_deadzone']:.3f}")
        deadzone_layout.addWidget(self.head_yaw_deadzone_label, 0, 2)

        deadzone_layout.addWidget(QLabel("Head Pitch Deadzone:"), 1, 0)
        self.head_pitch_deadzone_slider = QSlider(Qt.Horizontal)
        self.head_pitch_deadzone_slider.setRange(0, 200)  # 0 to 0.20
        self.head_pitch_deadzone_slider.setValue(int(self.config['calibration']['head_pitch_deadzone'] * 1000))  # Scale by 1000
        self.head_pitch_deadzone_slider.valueChanged.connect(self.on_head_pitch_deadzone_changed)
        deadzone_layout.addWidget(self.head_pitch_deadzone_slider, 1, 1)

        self.head_pitch_deadzone_label = QLabel(f"{self.config['calibration']['head_pitch_deadzone']:.3f}")
        deadzone_layout.addWidget(self.head_pitch_deadzone_label, 1, 2)

        deadzone_layout.addWidget(QLabel("Head Roll Deadzone:"), 2, 0)
        self.head_roll_deadzone_slider = QSlider(Qt.Horizontal)
        self.head_roll_deadzone_slider.setRange(0, 200)  # 0 to 0.20
        self.head_roll_deadzone_slider.setValue(int(self.config['calibration']['head_roll_deadzone'] * 1000))  # Scale by 1000
        self.head_roll_deadzone_slider.valueChanged.connect(self.on_head_roll_deadzone_changed)
        deadzone_layout.addWidget(self.head_roll_deadzone_slider, 2, 1)

        self.head_roll_deadzone_label = QLabel(f"{self.config['calibration']['head_roll_deadzone']:.3f}")
        deadzone_layout.addWidget(self.head_roll_deadzone_label, 2, 2)

        # Eye deadzones
        deadzone_layout.addWidget(QLabel("Eye Left Deadzone:"), 3, 0)
        self.eye_left_deadzone_slider = QSlider(Qt.Horizontal)
        self.eye_left_deadzone_slider.setRange(0, 200)  # 0 to 0.20
        self.eye_left_deadzone_slider.setValue(int(self.config['calibration']['eye_left_deadzone'] * 1000))  # Scale by 1000
        self.eye_left_deadzone_slider.valueChanged.connect(self.on_eye_left_deadzone_changed)
        deadzone_layout.addWidget(self.eye_left_deadzone_slider, 3, 1)

        self.eye_left_deadzone_label = QLabel(f"{self.config['calibration']['eye_left_deadzone']:.3f}")
        deadzone_layout.addWidget(self.eye_left_deadzone_label, 3, 2)

        deadzone_layout.addWidget(QLabel("Eye Right Deadzone:"), 4, 0)
        self.eye_right_deadzone_slider = QSlider(Qt.Horizontal)
        self.eye_right_deadzone_slider.setRange(0, 200)  # 0 to 0.20
        self.eye_right_deadzone_slider.setValue(int(self.config['calibration']['eye_right_deadzone'] * 1000))  # Scale by 1000
        self.eye_right_deadzone_slider.valueChanged.connect(self.on_eye_right_deadzone_changed)
        deadzone_layout.addWidget(self.eye_right_deadzone_slider, 4, 1)

        self.eye_right_deadzone_label = QLabel(f"{self.config['calibration']['eye_right_deadzone']:.3f}")
        deadzone_layout.addWidget(self.eye_right_deadzone_label, 4, 2)

        # Mouth deadzones
        deadzone_layout.addWidget(QLabel("Mouth Open Deadzone:"), 5, 0)
        self.mouth_open_deadzone_slider = QSlider(Qt.Horizontal)
        self.mouth_open_deadzone_slider.setRange(0, 200)  # 0 to 0.20
        self.mouth_open_deadzone_slider.setValue(int(self.config['calibration']['mouth_open_deadzone'] * 1000))  # Scale by 1000
        self.mouth_open_deadzone_slider.valueChanged.connect(self.on_mouth_open_deadzone_changed)
        deadzone_layout.addWidget(self.mouth_open_deadzone_slider, 5, 1)

        self.mouth_open_deadzone_label = QLabel(f"{self.config['calibration']['mouth_open_deadzone']:.3f}")
        deadzone_layout.addWidget(self.mouth_open_deadzone_label, 5, 2)

        deadzone_layout.addWidget(QLabel("Mouth Wide Deadzone:"), 6, 0)
        self.mouth_wide_deadzone_slider = QSlider(Qt.Horizontal)
        self.mouth_wide_deadzone_slider.setRange(0, 200)  # 0 to 0.20
        self.mouth_wide_deadzone_slider.setValue(int(self.config['calibration']['mouth_wide_deadzone'] * 1000))  # Scale by 1000
        self.mouth_wide_deadzone_slider.valueChanged.connect(self.on_mouth_wide_deadzone_changed)
        deadzone_layout.addWidget(self.mouth_wide_deadzone_slider, 6, 1)

        self.mouth_wide_deadzone_label = QLabel(f"{self.config['calibration']['mouth_wide_deadzone']:.3f}")
        deadzone_layout.addWidget(self.mouth_wide_deadzone_label, 6, 2)

        layout.addWidget(deadzone_group)

        # Precision mode settings
        precision_group = QGroupBox("Precision Mode Settings")
        precision_layout = QVBoxLayout(precision_group)

        self.precision_toggle = QCheckBox("Enable Precision Mode")
        self.precision_toggle.setChecked(self.config['precision']['enabled'])
        self.precision_toggle.stateChanged.connect(self.on_precision_toggle)
        precision_layout.addWidget(self.precision_toggle)

        precision_sub_layout = QHBoxLayout()

        precision_sub_layout.addWidget(QLabel("Precision Sensitivity:"))
        self.precision_sensitivity_slider = QSlider(Qt.Horizontal)
        self.precision_sensitivity_slider.setRange(100, 300)  # 1.0 to 3.0
        self.precision_sensitivity_slider.setValue(int(self.config['precision']['sensitivity_multiplier'] * 100))
        self.precision_sensitivity_slider.valueChanged.connect(self.on_precision_sensitivity_changed)
        precision_sub_layout.addWidget(self.precision_sensitivity_slider)

        self.precision_sensitivity_label = QLabel(f"{self.config['precision']['sensitivity_multiplier']:.2f}")
        precision_sub_layout.addWidget(self.precision_sensitivity_label)

        precision_layout.addLayout(precision_sub_layout)

        # Noise reduction settings
        noise_layout = QHBoxLayout()
        self.noise_reduction_toggle = QCheckBox("Enable Noise Reduction")
        self.noise_reduction_toggle.setChecked(self.config['precision']['noise_reduction_enabled'])
        self.noise_reduction_toggle.stateChanged.connect(self.on_noise_reduction_toggle)
        noise_layout.addWidget(self.noise_reduction_toggle)

        noise_layout.addWidget(QLabel("Noise Threshold:"))
        self.noise_threshold_slider = QSlider(Qt.Horizontal)
        self.noise_threshold_slider.setRange(0, 100)  # 0.00 to 0.10
        self.noise_threshold_slider.setValue(int(self.config['precision']['noise_threshold'] * 1000))  # Scale by 1000
        self.noise_threshold_slider.valueChanged.connect(self.on_noise_threshold_changed)
        noise_layout.addWidget(self.noise_threshold_slider)

        self.noise_threshold_label = QLabel(f"{self.config['precision']['noise_threshold']:.3f}")
        noise_layout.addWidget(self.noise_threshold_label)

        precision_layout.addLayout(noise_layout)

        layout.addWidget(precision_group)

        # Virtual camera settings
        virtual_camera_group = QGroupBox("Virtual Camera Settings")
        virtual_camera_layout = QVBoxLayout(virtual_camera_group)

        self.virtual_camera_toggle = QCheckBox("Enable Virtual Camera Output")
        self.virtual_camera_toggle.setChecked(self.config['virtual_camera']['enabled'])
        self.virtual_camera_toggle.stateChanged.connect(self.on_virtual_camera_toggle)
        virtual_camera_layout.addWidget(self.virtual_camera_toggle)

        # Resolution and FPS controls
        resolution_layout = QHBoxLayout()
        resolution_layout.addWidget(QLabel("Resolution:"))

        self.virtual_camera_resolution_combo = QComboBox()
        resolutions = [
            "640x480",   # VGA
            "1280x720",  # HD 720p
            "1920x1080"  # Full HD 1080p
        ]
        for res in resolutions:
            self.virtual_camera_resolution_combo.addItem(res)

        # Set current resolution based on config
        current_res = f"{self.config['virtual_camera']['width']}x{self.config['virtual_camera']['height']}"
        idx = self.virtual_camera_resolution_combo.findText(current_res)
        if idx >= 0:
            self.virtual_camera_resolution_combo.setCurrentIndex(idx)

        self.virtual_camera_resolution_combo.currentTextChanged.connect(self.on_virtual_camera_resolution_changed)
        resolution_layout.addWidget(self.virtual_camera_resolution_combo)

        resolution_layout.addWidget(QLabel("FPS:"))
        self.virtual_camera_fps_combo = QComboBox()
        fps_values = ["15", "20", "30", "60"]
        for fps in fps_values:
            self.virtual_camera_fps_combo.addItem(fps)

        # Set current FPS based on config
        self.virtual_camera_fps_combo.setCurrentText(str(self.config['virtual_camera']['fps']))
        self.virtual_camera_fps_combo.currentTextChanged.connect(self.on_virtual_camera_fps_changed)

        resolution_layout.addWidget(self.virtual_camera_fps_combo)
        virtual_camera_layout.addLayout(resolution_layout)

        layout.addWidget(virtual_camera_group)

        # Tracking data display
        tracking_data_group = QGroupBox("Tracking Data")
        tracking_data_layout = QVBoxLayout(tracking_data_group)

        self.tracking_data_label = QLabel("No data yet")
        self.tracking_data_label.setAlignment(Qt.AlignLeft)
        tracking_data_label_scroll = QScrollArea()
        tracking_data_label_scroll.setWidget(self.tracking_data_label)
        tracking_data_label_scroll.setWidgetResizable(True)
        tracking_data_layout.addWidget(tracking_data_label_scroll)

        layout.addWidget(tracking_data_group)

        return tab
    
    def create_output_tab(self):
        """Create the output control tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # VMC (VSeeFace) settings
        vmc_group = QGroupBox("VSeeFace (VMC Protocol)")
        vmc_layout = QGridLayout(vmc_group)
        
        self.vmc_enable = QCheckBox("Enable VMC Output")
        self.vmc_enable.setChecked(self.config['vmc']['enabled'])
        vmc_layout.addWidget(self.vmc_enable, 0, 0, 1, 2)
        
        vmc_layout.addWidget(QLabel("Host:"), 1, 0)
        self.vmc_host = QLabel(self.config['vmc']['host'])
        vmc_layout.addWidget(self.vmc_host, 1, 1)
        
        vmc_layout.addWidget(QLabel("Port:"), 2, 0)
        self.vmc_port = QLabel(str(self.config['vmc']['port']))
        vmc_layout.addWidget(self.vmc_port, 2, 1)
        
        self.vmc_status = QLabel("Status: Disconnected")
        vmc_layout.addWidget(self.vmc_status, 3, 0, 1, 2)
        
        layout.addWidget(vmc_group)
        
        # VTS (VTube Studio) settings
        vts_group = QGroupBox("VTube Studio (WebSocket)")
        vts_layout = QGridLayout(vts_group)
        
        self.vts_enable = QCheckBox("Enable VTS Output")
        self.vts_enable.setChecked(self.config['vts']['enabled'])
        vts_layout.addWidget(self.vts_enable, 0, 0, 1, 2)
        
        vts_layout.addWidget(QLabel("Host:"), 1, 0)
        self.vts_host = QLabel(self.config['vts']['host'])
        vts_layout.addWidget(self.vts_host, 1, 1)
        
        vts_layout.addWidget(QLabel("Port:"), 2, 0)
        self.vts_port = QLabel(str(self.config['vts']['port']))
        vts_layout.addWidget(self.vts_port, 2, 1)
        
        self.vts_status = QLabel("Status: Disconnected")
        vts_layout.addWidget(self.vts_status, 3, 0, 1, 2)
        
        layout.addWidget(vts_group)
        
        return tab
    
    def init_tracking(self):
        """Initialize tracking components."""
        try:
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

            # Update status labels
            self.update_sender_statuses()

        except Exception as e:
            logging.error(f"Error initializing tracking components: {e}")
            QMessageBox.critical(self, "Error", f"Error initializing tracking components: {e}")
    
    def update_camera_list(self):
        """Update the list of available cameras."""
        if self.camera:
            available_cameras = self.camera.get_available_cameras()
        else:
            # Create temporary camera to get available cameras
            temp_camera = CameraCapture()
            available_cameras = temp_camera.get_available_cameras()
            temp_camera.release()
        
        self.camera_combo.clear()
        for i in available_cameras:
            self.camera_combo.addItem(f"Camera {i}", i)
        
        # Set default camera
        default_idx = 0
        for i, cam_idx in enumerate(available_cameras):
            if cam_idx == self.config['camera']['default_camera_index']:
                default_idx = i
                break
        self.camera_combo.setCurrentIndex(default_idx)
        
        if available_cameras:
            self.start_btn.setEnabled(True)
        else:
            self.start_btn.setEnabled(False)
            QMessageBox.warning(self, "Warning", "No cameras found!")
    
    @pyqtSlot()
    def on_camera_changed(self):
        """Handle camera selection change."""
        if self.camera and self.tracking_worker and self.tracking_worker.running:
            # If tracking is running, stop it first
            self.stop_tracking()
            
        # Update camera
        selected_idx = self.camera_combo.currentData()
        if selected_idx is not None and self.camera:
            self.camera.set_camera_index(selected_idx)
    
    @pyqtSlot(int)
    def on_smoothing_alpha_changed(self, value):
        """Handle smoothing alpha slider change."""
        alpha = value / 100.0
        self.smoothing_alpha_label.setText(f"{alpha:.2f}")
        if self.smoother:
            self.smoother.update_alpha(alpha)
    
    @pyqtSlot(int)
    def on_smoothing_toggle(self, state):
        """Handle smoothing toggle."""
        enabled = bool(state)
        if self.smoother:
            if enabled:
                self.smoother.enabled = True
            else:
                self.smoother.enabled = False
                self.smoother.reset()  # Reset to prevent jumps when re-enabled
    
    def start_tracking(self):
        """Start the face tracking process."""
        if self.tracking_worker and self.tracking_worker.running:
            return  # Already running

        # Get selected camera index
        selected_idx = self.camera_combo.currentData()
        if selected_idx is None:
            QMessageBox.warning(self, "Warning", "Please select a camera first!")
            return

        # Initialize camera if not already done
        if not self.camera:
            try:
                self.camera = CameraCapture(
                    camera_index=selected_idx,
                    frame_width=self.config['camera']['frame_width'],
                    frame_height=self.config['camera']['frame_height']
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error opening camera: {e}")
                return

        # Test the camera connection
        test_frame = self.camera.get_frame()
        if test_frame is None:
            reply = QMessageBox.question(self, "Camera Issue",
                                        "Cannot access the camera. Continue anyway in test mode?",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                if self.camera:
                    self.camera.release()
                return

        # Update camera if needed
        if self.camera.camera_index != selected_idx:
            self.camera.set_camera_index(selected_idx)

        # Create and start tracking worker
        vmc_enabled = self.vmc_enable.isChecked()
        vts_enabled = self.vts_enable.isChecked()

        # Initialize virtual camera if enabled
        virtual_camera = None
        if self.config.get('virtual_camera', {}).get('enabled', False):
            virtual_camera = create_virtual_camera(
                width=self.config['camera']['frame_width'],
                height=self.config['camera']['frame_height'],
                fps=self.config['virtual_camera']['fps']
            )
            if virtual_camera:
                virtual_camera.enable_output(True)
                logging.info("Virtual camera initialized in GUI mode")

        self.tracking_worker = TrackingWorker(
            self.camera, self.face_tracker, self.smoother, self.mapper,
            self.calibrator, self.precision_mode, virtual_camera,
            self.vmc_sender, self.vts_sender,
            vmc_enabled, vts_enabled
        )

        # Connect signals
        self.tracking_worker.frame_processed.connect(self.update_preview)
        self.tracking_worker.tracking_data_ready.connect(self.update_tracking_data)
        # Set up a timer to periodically update calibration status if calibrating
        self.calibration_timer = QTimer()
        self.calibration_timer.timeout.connect(self.update_calibration_status)
        self.calibration_timer.start(100)  # Update every 100ms

        self.tracking_worker.start()

        # Update button states
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        self.status_bar.showMessage("Tracking started")
        logging.info("Tracking started")
    
    def stop_tracking(self):
        """Stop the face tracking process."""
        if self.tracking_worker and self.tracking_worker.running:
            self.tracking_worker.stop()
            self.tracking_worker.wait()  # Wait for thread to finish
            # Release virtual camera if it exists in the worker
            if hasattr(self.tracking_worker, 'virtual_camera') and self.tracking_worker.virtual_camera:
                self.tracking_worker.virtual_camera.release()
            self.tracking_worker = None

        # Stop the calibration timer if it exists
        if hasattr(self, 'calibration_timer'):
            self.calibration_timer.stop()
            delattr(self, 'calibration_timer')

        # Update button states
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        self.status_bar.showMessage("Tracking stopped")
        logging.info("Tracking stopped")
    
    @pyqtSlot(object)
    def update_preview(self, frame):
        """Update the camera preview."""
        if frame is not None:
            # Convert frame to QImage
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            
            # Scale pixmap to fit label while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.preview_label.width(),
                self.preview_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            self.preview_label.setPixmap(scaled_pixmap)
    
    def start_calibration(self):
        """Start the calibration process."""
        if self.calibrator and not self.calibrator.is_calibrating:
            self.calibrator.start_calibration()
            self.calibrate_btn.setText("Calibrating...")
            self.calibrate_btn.setEnabled(False)
            self.status_bar.showMessage("Calibration started. Please look straight ahead with a neutral expression.")
            logging.info("Calibration started")

    def reset_calibration(self):
        """Reset the calibration."""
        if self.calibrator:
            self.calibrator.reset_calibration()
            self.calibration_status_label.setText("Status: Not calibrated")
            self.status_bar.showMessage("Calibration reset")
            logging.info("Calibration reset")

    def update_calibration_status(self):
        """Update the calibration status display."""
        if self.calibrator:
            status = self.calibrator.get_calibration_status()
            self.calibration_status_label.setText(f"Status: {status}")

            # Update the calibrate button state
            if self.calibrator.is_calibrating:
                self.calibrate_btn.setText(f"Calibrating... {int(min(100, (self.calibrator.current_sample_count / self.calibrator.required_samples) * 100))}%")
            else:
                self.calibrate_btn.setText("Start Calibration")
                self.calibrate_btn.setEnabled(True)

    def update_tracking_data(self, tracking_data):
        """Update the tracking data display."""
        if tracking_data:
            data_text = f"""
            <b>Tracking Data:</b><br>
            Face Detected: {tracking_data.face_detected}<br>
            Calibrated: {self.calibrator.calibration_data.is_calibrated if self.calibrator else False}<br>
            Precision Mode: {self.precision_mode.enabled if self.precision_mode else False}<br>
            <br>
            <b>Head Rotation:</b><br>
            Yaw: {tracking_data.head_yaw:.3f}<br>
            Pitch: {tracking_data.head_pitch:.3f}<br>
            Roll: {tracking_data.head_roll:.3f}<br>
            <br>
            <b>Eyes:</b><br>
            Left Eye: {tracking_data.eye_left:.3f}<br>
            Right Eye: {tracking_data.eye_right:.3f}<br>
            <br>
            <b>Mouth:</b><br>
            Open: {tracking_data.mouth_open:.3f}<br>
            Wide: {tracking_data.mouth_wide:.3f}
            """
            self.tracking_data_label.setText(data_text)

    def on_head_yaw_sensitivity_changed(self, value):
        """Handle head yaw sensitivity slider change."""
        multiplier = value / 100.0
        self.head_yaw_sensitivity_label.setText(f"{multiplier:.2f}")
        if hasattr(self, 'mapper') and self.mapper:
            self.mapper.update_sensitivity(head_yaw_multiplier=multiplier)
        if hasattr(self, 'config') and self.config:
            self.config['calibration']['head_yaw_multiplier'] = multiplier

    def on_head_pitch_sensitivity_changed(self, value):
        """Handle head pitch sensitivity slider change."""
        multiplier = value / 100.0
        self.head_pitch_sensitivity_label.setText(f"{multiplier:.2f}")
        if hasattr(self, 'mapper') and self.mapper:
            self.mapper.update_sensitivity(head_pitch_multiplier=multiplier)
        if hasattr(self, 'config') and self.config:
            self.config['calibration']['head_pitch_multiplier'] = multiplier

    def on_head_roll_sensitivity_changed(self, value):
        """Handle head roll sensitivity slider change."""
        multiplier = value / 100.0
        self.head_roll_sensitivity_label.setText(f"{multiplier:.2f}")
        if hasattr(self, 'mapper') and self.mapper:
            self.mapper.update_sensitivity(head_roll_multiplier=multiplier)
        if hasattr(self, 'config') and self.config:
            self.config['calibration']['head_roll_multiplier'] = multiplier

    def on_eye_left_sensitivity_changed(self, value):
        """Handle eye left sensitivity slider change."""
        multiplier = value / 100.0
        self.eye_left_sensitivity_label.setText(f"{multiplier:.2f}")
        if hasattr(self, 'mapper') and self.mapper:
            self.mapper.update_sensitivity(eye_left_multiplier=multiplier)
        if hasattr(self, 'config') and self.config:
            self.config['calibration']['eye_left_multiplier'] = multiplier

    def on_eye_right_sensitivity_changed(self, value):
        """Handle eye right sensitivity slider change."""
        multiplier = value / 100.0
        self.eye_right_sensitivity_label.setText(f"{multiplier:.2f}")
        if hasattr(self, 'mapper') and self.mapper:
            self.mapper.update_sensitivity(eye_right_multiplier=multiplier)
        if hasattr(self, 'config') and self.config:
            self.config['calibration']['eye_right_multiplier'] = multiplier

    def on_mouth_open_sensitivity_changed(self, value):
        """Handle mouth open sensitivity slider change."""
        multiplier = value / 100.0
        self.mouth_open_sensitivity_label.setText(f"{multiplier:.2f}")
        if hasattr(self, 'mapper') and self.mapper:
            self.mapper.update_sensitivity(mouth_open_multiplier=multiplier)
        if hasattr(self, 'config') and self.config:
            self.config['calibration']['mouth_open_multiplier'] = multiplier

    def on_mouth_wide_sensitivity_changed(self, value):
        """Handle mouth wide sensitivity slider change."""
        multiplier = value / 100.0
        self.mouth_wide_sensitivity_label.setText(f"{multiplier:.2f}")
        if hasattr(self, 'mapper') and self.mapper:
            self.mapper.update_sensitivity(mouth_wide_multiplier=multiplier)
        if hasattr(self, 'config') and self.config:
            self.config['calibration']['mouth_wide_multiplier'] = multiplier

    def on_head_yaw_deadzone_changed(self, value):
        """Handle head yaw deadzone slider change."""
        deadzone = value / 1000.0
        self.head_yaw_deadzone_label.setText(f"{deadzone:.3f}")
        if hasattr(self, 'mapper') and self.mapper:
            self.mapper.update_deadzones(head_yaw_deadzone=deadzone)
        if hasattr(self, 'config') and self.config:
            self.config['calibration']['head_yaw_deadzone'] = deadzone

    def on_head_pitch_deadzone_changed(self, value):
        """Handle head pitch deadzone slider change."""
        deadzone = value / 1000.0
        self.head_pitch_deadzone_label.setText(f"{deadzone:.3f}")
        if hasattr(self, 'mapper') and self.mapper:
            self.mapper.update_deadzones(head_pitch_deadzone=deadzone)
        if hasattr(self, 'config') and self.config:
            self.config['calibration']['head_pitch_deadzone'] = deadzone

    def on_head_roll_deadzone_changed(self, value):
        """Handle head roll deadzone slider change."""
        deadzone = value / 1000.0
        self.head_roll_deadzone_label.setText(f"{deadzone:.3f}")
        if hasattr(self, 'mapper') and self.mapper:
            self.mapper.update_deadzones(head_roll_deadzone=deadzone)
        if hasattr(self, 'config') and self.config:
            self.config['calibration']['head_roll_deadzone'] = deadzone

    def on_eye_left_deadzone_changed(self, value):
        """Handle eye left deadzone slider change."""
        deadzone = value / 1000.0
        self.eye_left_deadzone_label.setText(f"{deadzone:.3f}")
        if hasattr(self, 'mapper') and self.mapper:
            self.mapper.update_deadzones(eye_left_deadzone=deadzone)
        if hasattr(self, 'config') and self.config:
            self.config['calibration']['eye_left_deadzone'] = deadzone

    def on_eye_right_deadzone_changed(self, value):
        """Handle eye right deadzone slider change."""
        deadzone = value / 1000.0
        self.eye_right_deadzone_label.setText(f"{deadzone:.3f}")
        if hasattr(self, 'mapper') and self.mapper:
            self.mapper.update_deadzones(eye_right_deadzone=deadzone)
        if hasattr(self, 'config') and self.config:
            self.config['calibration']['eye_right_deadzone'] = deadzone

    def on_mouth_open_deadzone_changed(self, value):
        """Handle mouth open deadzone slider change."""
        deadzone = value / 1000.0
        self.mouth_open_deadzone_label.setText(f"{deadzone:.3f}")
        if hasattr(self, 'mapper') and self.mapper:
            self.mapper.update_deadzones(mouth_open_deadzone=deadzone)
        if hasattr(self, 'config') and self.config:
            self.config['calibration']['mouth_open_deadzone'] = deadzone

    def on_mouth_wide_deadzone_changed(self, value):
        """Handle mouth wide deadzone slider change."""
        deadzone = value / 1000.0
        self.mouth_wide_deadzone_label.setText(f"{deadzone:.3f}")
        if hasattr(self, 'mapper') and self.mapper:
            self.mapper.update_deadzones(mouth_wide_deadzone=deadzone)
        if hasattr(self, 'config') and self.config:
            self.config['calibration']['mouth_wide_deadzone'] = deadzone

    def on_precision_toggle(self, state):
        """Handle precision mode toggle."""
        enabled = bool(state)
        if hasattr(self, 'precision_mode') and self.precision_mode:
            if enabled:
                self.precision_mode.enable_precision_mode(self.config['precision']['sensitivity_multiplier'])
                self.status_bar.showMessage("Precision mode enabled")
            else:
                self.precision_mode.disable_precision_mode()
                self.status_bar.showMessage("Precision mode disabled")
        if hasattr(self, 'config') and self.config:
            self.config['precision']['enabled'] = enabled

    def on_precision_sensitivity_changed(self, value):
        """Handle precision sensitivity slider change."""
        multiplier = value / 100.0
        self.precision_sensitivity_label.setText(f"{multiplier:.2f}")
        if hasattr(self, 'precision_mode') and self.precision_mode and self.precision_mode.enabled:
            self.precision_mode.set_precision_params(sensitivity_multiplier=multiplier)
        if hasattr(self, 'config') and self.config:
            self.config['precision']['sensitivity_multiplier'] = multiplier

    def on_noise_reduction_toggle(self, state):
        """Handle noise reduction toggle."""
        enabled = bool(state)
        if hasattr(self, 'precision_mode') and self.precision_mode:
            self.precision_mode.set_precision_params(noise_reduction_enabled=enabled)
        if hasattr(self, 'config') and self.config:
            self.config['precision']['noise_reduction_enabled'] = enabled

    def on_noise_threshold_changed(self, value):
        """Handle noise threshold slider change."""
        threshold = value / 1000.0
        self.noise_threshold_label.setText(f"{threshold:.3f}")
        if hasattr(self, 'precision_mode') and self.precision_mode:
            self.precision_mode.set_precision_params(noise_threshold=threshold)
        if hasattr(self, 'config') and self.config:
            self.config['precision']['noise_threshold'] = threshold

    def on_virtual_camera_toggle(self, state):
        """Handle virtual camera toggle."""
        enabled = bool(state)
        if hasattr(self, 'config') and self.config:
            self.config['virtual_camera']['enabled'] = enabled

    def on_virtual_camera_resolution_changed(self, resolution):
        """Handle virtual camera resolution change."""
        width, height = resolution.split('x')
        width = int(width)
        height = int(height)

        if hasattr(self, 'config') and self.config:
            self.config['virtual_camera']['width'] = width
            self.config['virtual_camera']['height'] = height

    def on_virtual_camera_fps_changed(self, fps):
        """Handle virtual camera FPS change."""
        fps = int(fps)

        if hasattr(self, 'config') and self.config:
            self.config['virtual_camera']['fps'] = fps

    def update_sender_statuses(self):
        """Update the status labels for senders."""
        if self.vmc_sender:
            status = "Connected" if self.vmc_sender.is_connected else "Disconnected"
            self.vmc_status.setText(f"Status: {status}")
        
        if self.vts_sender:
            status = "Connected" if self.vts_sender.is_connected else "Disconnected"
            self.vts_status.setText(f"Status: {status}")
    
    def closeEvent(self, event):
        """Handle application close event."""
        # Stop tracking if running
        if self.tracking_worker and self.tracking_worker.running:
            self.stop_tracking()

        # Release camera
        if self.camera:
            self.camera.release()

        # Disconnect senders
        if self.vmc_sender:
            self.vmc_sender.disconnect()

        if self.vts_sender:
            self.vts_sender.disconnect()

        # Clean up additional components
        self.calibrator = None
        self.precision_mode = None

        event.accept()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()