"""
VTS sender module for VTuber face tracking system.
Sends face tracking data to VTube Studio via WebSocket API.
"""
import websocket
import json
import threading
import time
import uuid
import logging
from typing import Dict, Any, Optional
import requests

class VTSSender:
    def __init__(self, host="127.0.0.1", port=8001, enabled=True):
        """
        Initialize VTS sender for VTube Studio communication.
        
        Args:
            host: Host address for VTube Studio WebSocket
            port: Port for VTube Studio WebSocket (default 8001)
            enabled: Whether VTS sending is enabled
        """
        self.host = host
        self.port = port
        self.url = f"ws://{host}:{port}"
        self.enabled = enabled
        self.ws = None
        self.is_connected = False
        self.auth_token = None
        self.plugin_name = "VTuber Tracker Plugin"
        self.plugin_developer = "VTuber Tracker"
        self.plugin_icon = ""  # Base64 encoded icon if needed
        self.session_id = None
        
        # Parameter values cache to avoid sending unchanged values
        self.param_cache = {}
        
        # Start WebSocket connection
        if self.enabled:
            self.connect()
    
    def connect(self):
        """Connect to VTube Studio via WebSocket."""
        try:
            # First, check if VTube Studio is running by making an HTTP request
            response = requests.get(f"http://{self.host}:{self.port}/api/getfolderinfo", timeout=2)
            if response.status_code != 200:
                logging.error("VTube Studio does not appear to be running")
                return False
        except requests.exceptions.RequestException:
            logging.error("Cannot connect to VTube Studio, make sure it's running")
            return False
        
        try:
            # Connect to WebSocket
            self.ws = websocket.WebSocketApp(
                self.url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            
            # Run WebSocket in a separate thread
            self.ws_thread = threading.Thread(target=self.ws.run_forever)
            self.ws_thread.daemon = True
            self.ws_thread.start()
            
            # Wait a bit for connection
            time.sleep(1)
            
            # Authenticate with VTube Studio
            if self.is_connected:
                self.authenticate()
            
            return self.is_connected
        except Exception as e:
            logging.error(f"Failed to connect to VTube Studio: {e}")
            return False
    
    def on_open(self, ws):
        """Called when WebSocket connection opens."""
        logging.info("Connected to VTube Studio WebSocket")
        self.is_connected = True
    
    def on_message(self, ws, message):
        """Handle incoming messages from VTube Studio."""
        try:
            data = json.loads(message)
            msg_type = data.get("messageType", "")
            
            if msg_type == "APIError":
                logging.error(f"VTube Studio API Error: {data.get('data', {}).get('errorIDMessage', 'Unknown error')}")
            elif msg_type == "AuthenticationToken":
                # Handle authentication token response
                self.auth_token = data.get("data", {}).get("authenticationToken")
                self.authenticate_with_token()
            elif msg_type == "AuthenticationResponse":
                # Check if authentication was successful
                if data.get("data", {}).get("authenticated", False):
                    logging.info("Successfully authenticated with VTube Studio")
                    self.session_id = data.get("data", {}).get("sessionID")
                else:
                    logging.error("Failed to authenticate with VTube Studio")
            elif msg_type == "CurrentModelParameters":
                # Handle parameter values response
                logging.debug(f"Received model parameters: {data}")
        except json.JSONDecodeError:
            logging.error(f"Invalid JSON received: {message}")
        except Exception as e:
            logging.error(f"Error handling message: {e}")
    
    def on_error(self, ws, error):
        """Handle WebSocket errors."""
        logging.error(f"WebSocket error: {error}")
        self.is_connected = False
        self.auth_token = None
    
    def on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket connection close."""
        logging.info(f"WebSocket connection closed: {close_msg}")
        self.is_connected = False
        self.auth_token = None
    
    def authenticate(self):
        """Request authentication token from VTube Studio."""
        if not self.is_connected:
            logging.error("Not connected to VTube Studio")
            return
        
        auth_request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": str(uuid.uuid4()),
            "messageType": "AuthenticationRequest",
            "data": {
                "pluginName": self.plugin_name,
                "pluginDeveloper": self.plugin_developer,
                "pluginIcon": self.plugin_icon
            }
        }
        
        self.ws.send(json.dumps(auth_request))
        logging.info("Authentication request sent to VTube Studio")
    
    def authenticate_with_token(self):
        """Authenticate using the received token."""
        if not self.auth_token:
            logging.error("No authentication token received")
            return
        
        auth_with_token_request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": str(uuid.uuid4()),
            "messageType": "AuthenticationRequest",
            "data": {
                "pluginName": self.plugin_name,
                "pluginDeveloper": self.plugin_developer,
                "pluginIcon": self.plugin_icon,
                "authenticationToken": self.auth_token
            }
        }
        
        self.ws.send(json.dumps(auth_with_token_request))
        logging.info("Authentication request with token sent to VTube Studio")
    
    def send_tracking_data(self, tracking_params: Dict[str, Any]):
        """
        Send tracking data to VTube Studio.
        
        Args:
            tracking_params: Dictionary containing VTS parameters
        """
        if not self.enabled or not self.is_connected or not self.ws:
            return
        
        try:
            # Prepare parameter updates
            param_updates = []
            
            for param_name, value in tracking_params.items():
                # Skip values that haven't changed significantly to reduce network traffic
                if param_name in self.param_cache:
                    if abs(self.param_cache[param_name] - value) < 0.01:  # Small threshold
                        continue
                
                self.param_cache[param_name] = value
                
                param_updates.append({
                    "id": param_name,
                    "value": value
                })
            
            # If no parameters changed significantly, skip sending
            if not param_updates:
                return
            
            # Send parameter updates to VTube Studio
            param_update_request = {
                "apiName": "VTubeStudioPublicAPI",
                "apiVersion": "1.0",
                "requestID": str(uuid.uuid4()),
                "messageType": "ParameterUpdateRequest",
                "data": {
                    "parameterValues": param_updates
                }
            }
            
            self.ws.send(json.dumps(param_update_request))
            
        except Exception as e:
            logging.error(f"Error sending tracking data to VTube Studio: {e}")
    
    def send_hotkey(self, hotkey_id: str):
        """
        Send a hotkey trigger to VTube Studio.
        
        Args:
            hotkey_id: ID of the hotkey to trigger
        """
        if not self.enabled or not self.is_connected or not self.ws:
            return
        
        hotkey_request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": str(uuid.uuid4()),
            "messageType": "HotkeyTriggerRequest",
            "data": {
                "hotkeyID": hotkey_id
            }
        }
        
        self.ws.send(json.dumps(hotkey_request))
    
    def get_current_model_parameters(self):
        """Get current model parameters from VTube Studio."""
        if not self.enabled or not self.is_connected or not self.ws:
            return None
        
        param_request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": str(uuid.uuid4()),
            "messageType": "GetCurrentModelParametersRequest"
        }
        
        self.ws.send(json.dumps(param_request))
    
    def disconnect(self):
        """Disconnect from VTube Studio."""
        if self.ws:
            self.ws.close()
        
        self.is_connected = False
        self.auth_token = None
        logging.info("Disconnected from VTube Studio")
    
    def enable(self):
        """Enable VTS sending."""
        self.enabled = True
        if not self.is_connected:
            self.connect()
        logging.info("VTS sending enabled")
    
    def disable(self):
        """Disable VTS sending."""
        self.enabled = False
        logging.info("VTS sending disabled")
    
    def update_connection(self, host: str, port: int):
        """
        Update connection settings.
        
        Args:
            host: New host address
            port: New port
        """
        self.disconnect()
        self.host = host
        self.port = port
        self.url = f"ws://{host}:{port}"
        if self.enabled:
            self.connect()

if __name__ == "__main__":
    # Test the VTS sender
    import time
    
    logging.basicConfig(level=logging.INFO)
    
    # Create VTS sender
    vts_sender = VTSSender(host="127.0.0.1", port=8001)
    
    # Wait for authentication
    time.sleep(3)
    
    # Test data
    test_params = {
        "ParamAngleX": 15.0,   # Head yaw
        "ParamAngleY": 10.0,   # Head pitch
        "ParamAngleZ": 5.0,    # Head roll
        "ParamEyeLOpen": 1.0,  # Left eye open
        "ParamEyeROpen": 1.0,  # Right eye open
        "ParamMouthOpenY": 0.0, # Mouth closed
        "ParamMouthForm": 0.0,  # Mouth shape
    }
    
    if vts_sender.is_connected:
        print("Testing VTS sender. Check if VTube Studio receives the data.")
        print("Sending test data 10 times with 1 second interval...")
        
        for i in range(10):
            print(f"Sending test data {i+1}/10")
            vts_sender.send_tracking_data(test_params)
            time.sleep(1)
        
        # Test with different values
        test_params["ParamMouthOpenY"] = 1.0  # Mouth open
        test_params["ParamEyeLOpen"] = 0.0    # Left eye closed
        test_params["ParamEyeROpen"] = 0.0    # Right eye closed
        
        print("\nSending mouth open and eye blink test...")
        for i in range(5):
            print(f"Sending expression test {i+1}/5")
            vts_sender.send_tracking_data(test_params)
            time.sleep(0.5)
        
        vts_sender.disconnect()
        print("Test completed.")
    else:
        print("Could not connect to VTube Studio. Make sure VTube Studio is running and API is enabled.")