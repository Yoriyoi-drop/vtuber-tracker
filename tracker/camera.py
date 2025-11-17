"""
Camera module for VTuber face tracking system.
Handles webcam capture and camera selection.
"""
import cv2
import logging

class CameraCapture:
    def __init__(self, camera_index=0, frame_width=640, frame_height=480):
        self.camera_index = camera_index
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.cap = None
        self.is_capturing = False
        
        # Initialize camera
        self.open_camera()
    
    def open_camera(self):
        """Open camera with specified parameters."""
        if self.cap is not None and self.cap.isOpened():
            self.release()
            
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera with index {self.camera_index}")
        
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        self.is_capturing = True
        logging.info(f"Camera opened successfully: index={self.camera_index}, "
                    f"resolution={self.frame_width}x{self.frame_height}")
    
    def get_frame(self):
        """Get a single frame from the camera."""
        if not self.is_capturing or self.cap is None:
            return None
            
        ret, frame = self.cap.read()
        if not ret:
            logging.warning("Failed to read frame from camera")
            return None
            
        return frame
    
    def get_available_cameras(self, max_cameras=10):
        """Detect available cameras."""
        available_cameras = []
        for i in range(max_cameras):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available_cameras.append(i)
                cap.release()
            else:
                break
        return available_cameras
    
    def set_camera_index(self, index):
        """Change camera index."""
        if self.camera_index != index:
            self.camera_index = index
            self.open_camera()
    
    def release(self):
        """Release camera resources."""
        if self.cap is not None:
            self.cap.release()
            self.is_capturing = False
            logging.info("Camera released successfully")
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        self.release()


if __name__ == "__main__":
    # Test the camera module
    import time
    
    logging.basicConfig(level=logging.INFO)
    
    try:
        camera = CameraCapture(camera_index=0)
        print(f"Available cameras: {camera.get_available_cameras()}")
        
        # Test frame capture
        for i in range(10):  # Capture 10 frames for testing
            frame = camera.get_frame()
            if frame is not None:
                print(f"Frame {i+1} captured: {frame.shape}")
            else:
                print(f"Failed to capture frame {i+1}")
            time.sleep(0.1)
        
        camera.release()
    except Exception as e:
        print(f"Error: {e}")