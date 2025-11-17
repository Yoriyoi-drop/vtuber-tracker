"""
VMC sender module for VTuber face tracking system.
Sends face tracking data to VSeeFace via OSC protocol.
"""
import socket
import time
import struct
import json
import logging
from pythonosc import udp_client
from pythonosc.osc_message_builder import OscMessageBuilder
import threading
from typing import Dict, Any, Optional

class VMCSender:
    def __init__(self, host="127.0.0.1", port=39539, enabled=True):
        """
        Initialize VMC sender for VSeeFace communication.
        
        Args:
            host: Host address for OSC communication
            port: Port for OSC communication (default 39539 for VSeeFace)
            enabled: Whether VMC sending is enabled
        """
        self.host = host
        self.port = port
        self.enabled = enabled
        self.client = None
        self.is_connected = False
        self.connect()
    
    def connect(self):
        """Connect to VSeeFace via OSC."""
        try:
            self.client = udp_client.SimpleUDPClient(self.host, self.port)
            self.is_connected = True
            logging.info(f"Connected to VSeeFace at {self.host}:{self.port}")
            return True
        except Exception as e:
            self.is_connected = False
            logging.error(f"Failed to connect to VSeeFace at {self.host}:{self.port}: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from VSeeFace."""
        self.is_connected = False
        self.client = None
        logging.info("Disconnected from VSeeFace")
    
    def send_tracking_data(self, tracking_params: Dict[str, Any]):
        """
        Send tracking data to VSeeFace via OSC.
        
        Args:
            tracking_params: Dictionary containing VMC parameters
        """
        if not self.enabled or not self.is_connected or not self.client:
            return
        
        try:
            # Send head position and rotation
            # VMC Protocol: /VMC/Ext/Root/Pos pos x y z
            # VMC Protocol: /VMC/Ext/Root/Rot rot rw rx ry rz
            # Head rotation
            if all(key in tracking_params for key in ["head_yaw", "head_pitch", "head_roll"]):
                # Convert radians to quaternion for VMC
                quat = self.euler_to_quaternion(
                    tracking_params["head_pitch"],  # pitch (x)
                    tracking_params["head_yaw"],    # yaw (y) 
                    tracking_params["head_roll"]    # roll (z)
                )
                
                self.client.send_message("/VMC/Ext/Root/Rot", [1.0, quat[1], quat[2], quat[3]])  # w, x, y, z
            
            # Send blendshape parameters
            blendshape_mappings = {
                "Blink_L": tracking_params.get("Blink_L", 0.0),
                "Blink_R": tracking_params.get("Blink_R", 0.0),
                "A": tracking_params.get("A", 0.0),  # Mouth open
                "I": tracking_params.get("I", 0.0),  # Mouth shape
                "U": tracking_params.get("U", 0.0),  # Mouth shape
                "E": tracking_params.get("E", 0.0),  # Mouth shape
                "O": tracking_params.get("O", 0.0),  # Mouth shape
                "Joy": tracking_params.get("Joy", 0.0)  # Smile
            }
            
            for blendshape_name, value in blendshape_mappings.items():
                self.client.send_message("/VMC/Ext/Blend/Val", [blendshape_name, value, 1])
            
            # Send additional face tracking parameters as custom blendshapes
            # These might not be standard but can be mapped in VSeeFace
            if "MouthSmileL" in tracking_params:
                self.client.send_message("/VMC/Ext/Blend/Val", ["MouthSmileL", tracking_params["MouthSmileL"], 1])
            if "MouthSmileR" in tracking_params:
                self.client.send_message("/VMC/Ext/Blend/Val", ["MouthSmileR", tracking_params["MouthSmileR"], 1])
                
        except Exception as e:
            logging.error(f"Error sending tracking data to VSeeFace: {e}")
    
    def send_raw_osc(self, address: str, value: Any):
        """
        Send a raw OSC message.
        
        Args:
            address: OSC address
            value: Value to send
        """
        if not self.enabled or not self.is_connected or not self.client:
            return
        
        try:
            self.client.send_message(address, value)
        except Exception as e:
            logging.error(f"Error sending raw OSC message to {address}: {e}")
    
    def euler_to_quaternion(self, roll: float, pitch: float, yaw: float):
        """
        Convert Euler angles to quaternion.
        
        Args:
            roll: Roll angle (rotation around x-axis)
            pitch: Pitch angle (rotation around y-axis)
            yaw: Yaw angle (rotation around z-axis)
            
        Returns:
            Quaternion as [w, x, y, z]
        """
        # Convert from normalized values to radians if needed
        # In our case, the values are already in radians (from face tracking)
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        
        w = cr * cp * cy + sr * sp * sy
        x = sr * cp * cy - cr * sp * sy
        y = cr * sp * cy + sr * cp * sy
        z = cr * cp * sy - sr * sp * cy
        
        return [w, x, y, z]
    
    def enable(self):
        """Enable VMC sending."""
        self.enabled = True
        logging.info("VMC sending enabled")
    
    def disable(self):
        """Disable VMC sending."""
        self.enabled = False
        logging.info("VMC sending disabled")
    
    def update_connection(self, host: str, port: int):
        """
        Update connection settings.
        
        Args:
            host: New host address
            port: New port
        """
        self.host = host
        self.port = port
        self.disconnect()
        self.connect()

# Test the VMC sender without math import issue
import math

if __name__ == "__main__":
    # Test the VMC sender
    import time
    
    logging.basicConfig(level=logging.INFO)
    
    # Create VMC sender
    vmc_sender = VMCSender(host="127.0.0.1", port=39539)
    
    # Test data
    test_params = {
        "head_yaw": 0.2,
        "head_pitch": -0.1,
        "head_roll": 0.05,
        "Blink_L": 0.0,
        "Blink_R": 0.0,
        "A": 0.0,  # Mouth open
        "I": 0.1,  # Mouth shape
        "U": 0.05,  # Mouth shape
        "E": 0.05,  # Mouth shape
        "O": 0.1,  # Mouth shape
        "Joy": 0.2  # Smile
    }
    
    print("Testing VMC sender. Check if VSeeFace receives the data.")
    print("Sending test data 10 times with 1 second interval...")
    
    for i in range(10):
        print(f"Sending test data {i+1}/10")
        vmc_sender.send_tracking_data(test_params)
        time.sleep(1)
    
    # Test with different values
    test_params["Blink_L"] = 1.0
    test_params["Blink_R"] = 1.0
    test_params["A"] = 0.8
    test_params["head_yaw"] = 0.5
    
    print("\nSending blink and mouth open test...")
    for i in range(5):
        print(f"Sending blink test {i+1}/5")
        vmc_sender.send_tracking_data(test_params)
        time.sleep(0.5)
    
    vmc_sender.disconnect()
    print("Test completed.")