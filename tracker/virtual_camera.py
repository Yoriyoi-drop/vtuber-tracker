"""
Virtual camera output module for VTuber face tracking system.
Provides virtual camera output for applications like OBS, Zoom, etc.
"""
import cv2
import numpy as np
import threading
import time
from typing import Optional
import logging

try:
    import pyfakewebcam  # For Linux-based virtual camera
    FAKWEBCAM_AVAILABLE = True
except ImportError:
    FAKWEBCAM_AVAILABLE = False
    logging.warning("pyfakewebcam not available. Virtual camera output will be limited.")

class VirtualCameraOutput:
    def __init__(self, width: int = 640, height: int = 480, fps: int = 30):
        self.width = width
        self.height = height
        self.fps = fps
        self.is_active = False
        self.output_thread = None
        self.current_frame = np.zeros((height, width, 3), dtype=np.uint8)
        self.frame_lock = threading.Lock()
        self.enabled = False
        
        # Initialize virtual camera if available
        self.virtual_cam = None
        if FAKWEBCAM_AVAILABLE:
            try:
                # Find an available video device (usually /dev/videoX)
                # This requires v4l2loopback to be set up
                import subprocess
                result = subprocess.run(['ls', '/dev/video*'], capture_output=True, text=True)
                video_devices = result.stdout.strip().split('\n') if result.returncode == 0 else []
                
                # Find the highest numbered device and use the next one
                max_num = 0
                for device in video_devices:
                    try:
                        num = int(device.split('video')[1])
                        if num > max_num:
                            max_num = num
                    except ValueError:
                        continue
                
                next_device = f"/dev/video{max_num + 1}"
                self.virtual_cam = pyfakewebcam.FakeWebcam(next_device, width, height)
                logging.info(f"Virtual camera initialized at {next_device}")
            except Exception as e:
                logging.error(f"Failed to initialize virtual camera: {e}")
                self.virtual_cam = None
        else:
            logging.warning("pyfakewebcam not installed. Install with: pip install pyfakewebcam")

    def enable_output(self, enabled: bool = True):
        """Enable or disable virtual camera output."""
        self.enabled = enabled
        if enabled and not self.is_active:
            self.start_output()
        elif not enabled:
            self.stop_output()

    def start_output(self):
        """Start the virtual camera output."""
        if self.is_active or not self.enabled:
            return
        
        self.is_active = True
        self.output_thread = threading.Thread(target=self._output_loop, daemon=True)
        self.output_thread.start()
        logging.info("Virtual camera output started")

    def stop_output(self):
        """Stop the virtual camera output."""
        if not self.is_active:
            return
        
        self.is_active = False
        if self.output_thread and self.output_thread.is_alive():
            self.output_thread.join(timeout=1.0)
        logging.info("Virtual camera output stopped")

    def _output_loop(self):
        """Main output loop to send frames to virtual camera."""
        while self.is_active and self.enabled:
            if self.virtual_cam:
                with self.frame_lock:
                    frame_copy = self.current_frame.copy()
                
                try:
                    self.virtual_cam.schedule_frame(frame_copy)
                except Exception as e:
                    logging.error(f"Error sending frame to virtual camera: {e}")
            
            # Control frame rate
            time.sleep(1.0 / self.fps)

    def send_frame(self, frame: np.ndarray):
        """Send a frame to the virtual camera."""
        if not self.enabled or not self.is_active:
            return
            
        with self.frame_lock:
            # Resize frame to match virtual camera dimensions if needed
            if frame.shape[0] != self.height or frame.shape[1] != self.width:
                frame = cv2.resize(frame, (self.width, self.height))
            
            # Ensure frame is in RGB format (pyfakewebcam expects RGB)
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                # If it's BGR, convert to RGB
                if np.array_equal(frame[:,:,0], frame[:,:,2]):  # Check if it's RGB
                    self.current_frame = frame
                else:  # It's BGR, convert to RGB
                    self.current_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                self.current_frame = frame

    def release(self):
        """Release virtual camera resources."""
        self.stop_output()
        if self.virtual_cam:
            # pyfakewebcam doesn't have a release method
            pass

    def is_available(self) -> bool:
        """Check if virtual camera output is available."""
        return self.virtual_cam is not None


# Alternative approach for Windows/macOS using different libraries
class WindowsVirtualCamera:
    """Virtual camera implementation for Windows using different approaches."""
    
    def __init__(self, width: int = 640, height: int = 480, fps: int = 30):
        self.width = width
        self.height = height
        self.fps = fps
        self.is_active = False
        self.current_frame = np.zeros((height, width, 3), dtype=np.uint8)
        self.enabled = False
        
        # On Windows, we might use different approaches like OBS Virtual Camera
        # or other virtual camera drivers
        logging.info("Windows virtual camera not fully implemented yet")
    
    def enable_output(self, enabled: bool = True):
        self.enabled = enabled
    
    def send_frame(self, frame: np.ndarray):
        if not self.enabled:
            return
        # Implementation would depend on specific Windows virtual camera solution
        pass
    
    def release(self):
        pass


class MacVirtualCamera:
    """Virtual camera implementation for macOS using different approaches."""
    
    def __init__(self, width: int = 640, height: int = 480, fps: int = 30):
        self.width = width
        self.height = height
        self.fps = fps
        self.is_active = False
        self.current_frame = np.zeros((height, width, 3), dtype=np.uint8)
        self.enabled = False
        
        # On macOS, we might use CamTwist, OBS Virtual Camera, or similar
        logging.info("macOS virtual camera not fully implemented yet")
    
    def enable_output(self, enabled: bool = True):
        self.enabled = enabled
    
    def send_frame(self, frame: np.ndarray):
        if not self.enabled:
            return
        # Implementation would depend on specific macOS virtual camera solution
        pass
    
    def release(self):
        pass


def create_virtual_camera(width: int = 640, height: int = 480, fps: int = 30):
    """Factory function to create appropriate virtual camera for the platform."""
    import platform
    system = platform.system().lower()
    
    if system == "linux":
        return VirtualCameraOutput(width, height, fps)
    elif system == "windows":
        return WindowsVirtualCamera(width, height, fps)
    elif system == "darwin":  # macOS
        return MacVirtualCamera(width, height, fps)
    else:
        logging.warning(f"Virtual camera not supported on {system}")
        return None


if __name__ == "__main__":
    # Test the virtual camera
    import time
    
    print("Testing Virtual Camera Output...")
    
    # Create virtual camera
    vcam = create_virtual_camera()
    if vcam:
        vcam.enable_output(True)
        
        # Create test frames
        for i in range(100):
            # Create a test frame with moving elements
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            center_x = int(320 + 100 * np.cos(i * 0.1))
            center_y = int(240 + 100 * np.sin(i * 0.1))
            
            cv2.circle(frame, (center_x, center_y), 50, (0, 255, 0), -1)
            cv2.putText(frame, f"Frame {i}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            vcam.send_frame(frame)
            time.sleep(1/30)  # 30 FPS
        
        vcam.release()
        print("Virtual camera test completed")
    else:
        print("Virtual camera not available on this platform")