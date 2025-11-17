"""
Landmarks to parameters mapping module for VTuber face tracking system.
Converts raw face tracking data to parameters suitable for VMC and VTS protocols.
"""
from .face_tracking import FaceTrackingData
import math
import logging

class LandmarksToParameters:
    def __init__(self):
        # Sensitivity multipliers for different tracking parameters
        self.head_rotation_multiplier = 1.0
        self.head_yaw_multiplier = 1.0
        self.head_pitch_multiplier = 1.0
        self.head_roll_multiplier = 1.0
        self.eye_blink_multiplier = 1.0
        self.eye_left_multiplier = 1.0
        self.eye_right_multiplier = 1.0
        self.mouth_open_multiplier = 1.0
        self.mouth_wide_multiplier = 1.0

        # Deadzone settings to filter small movements
        self.head_yaw_deadzone = 0.05
        self.head_pitch_deadzone = 0.05
        self.head_roll_deadzone = 0.05
        self.eye_left_deadzone = 0.05
        self.eye_right_deadzone = 0.05
        self.mouth_open_deadzone = 0.05
        self.mouth_wide_deadzone = 0.05

        # VMC parameter mappings
        self.vmc_blendshapes = {
            "Blink_L": "eye_left",
            "Blink_R": "eye_right",
            "A": "mouth_open",  # A sound for mouth open
            "I": "mouth_wide",  # I sound for mouth shape
            "U": "mouth_wide",  # U sound for mouth shape
            "E": "mouth_wide",  # E sound for mouth shape
            "O": "mouth_wide",  # O sound for mouth shape
            "Joy": "mouth_wide",  # Expression for smiling
        }

        # VTS parameter mappings
        self.vts_parameters = {
            "ParamAngleX": "head_yaw",      # Horizontal head rotation
            "ParamAngleY": "head_pitch",    # Vertical head rotation
            "ParamAngleZ": "head_roll",     # Tilt head rotation
            "ParamEyeLOpen": "eye_left",    # Left eye open/close
            "ParamEyeROpen": "eye_right",   # Right eye open/close
            "ParamMouthOpenY": "mouth_open", # Mouth open/close
            "ParamMouthForm": "mouth_wide",  # Mouth shape/widen
        }

    def apply_deadzone(self, value: float, deadzone: float) -> float:
        """
        Apply deadzone to a value to filter small movements.

        Args:
            value: Input value
            deadzone: Deadzone threshold

        Returns:
            Value with deadzone applied
        """
        if abs(value) < deadzone:
            return 0.0
        else:
            # Rescale the value to account for the deadzone
            if value >= 0:
                return (value - deadzone) / (1.0 - deadzone)
            else:
                return (value + deadzone) / (1.0 - deadzone)

    def map_to_vmc_params(self, tracking_data: FaceTrackingData) -> dict:
        """
        Map tracking data to VMC protocol parameters.

        Args:
            tracking_data: Raw face tracking data

        Returns:
            Dictionary of VMC parameters
        """
        vmc_params = {}

        # Apply deadzones and multipliers
        head_yaw = self.apply_deadzone(tracking_data.head_yaw, self.head_yaw_deadzone)
        head_pitch = self.apply_deadzone(tracking_data.head_pitch, self.head_pitch_deadzone)
        head_roll = self.apply_deadzone(tracking_data.head_roll, self.head_roll_deadzone)
        eye_left = self.apply_deadzone(tracking_data.eye_left, self.eye_left_deadzone)
        eye_right = self.apply_deadzone(tracking_data.eye_right, self.eye_right_deadzone)
        mouth_open = self.apply_deadzone(tracking_data.mouth_open, self.mouth_open_deadzone)
        mouth_wide = self.apply_deadzone(tracking_data.mouth_wide, self.mouth_wide_deadzone)

        # Map head rotations with individual axis multipliers
        vmc_params["head_yaw"] = head_yaw * self.head_yaw_multiplier
        vmc_params["head_pitch"] = head_pitch * self.head_pitch_multiplier
        vmc_params["head_roll"] = head_roll * self.head_roll_multiplier

        # Map eye blinks and facial expressions with individual multipliers
        vmc_params["Blink_L"] = max(0.0, min(1.0, eye_left * self.eye_left_multiplier))
        vmc_params["Blink_R"] = max(0.0, min(1.0, eye_right * self.eye_right_multiplier))

        # Map mouth parameters to multiple blendshapes for better effect
        adjusted_mouth_open = max(0.0, min(1.0, mouth_open * self.mouth_open_multiplier))
        adjusted_mouth_wide = max(0.0, min(1.0, mouth_wide * self.mouth_wide_multiplier))

        # Map to multiple mouth blendshapes for VMC
        vmc_params["A"] = min(1.0, adjusted_mouth_open * 1.5)  # A for open mouth
        vmc_params["I"] = min(1.0, adjusted_mouth_wide * 0.5)  # I for mouth shape
        vmc_params["U"] = min(1.0, adjusted_mouth_wide * 0.5)  # U for mouth shape
        vmc_params["E"] = min(1.0, adjusted_mouth_wide * 0.3)  # E for mouth shape
        vmc_params["O"] = min(1.0, adjusted_mouth_open * 0.8)  # O for rounded mouth

        # Add smile parameter
        vmc_params["Joy"] = min(1.0, adjusted_mouth_wide * 1.2)  # Joy for smiling expression

        return vmc_params

    def map_to_vts_params(self, tracking_data: FaceTrackingData) -> dict:
        """
        Map tracking data to VTS protocol parameters.

        Args:
            tracking_data: Raw face tracking data

        Returns:
            Dictionary of VTS parameters
        """
        vts_params = {}

        # Apply deadzones and multipliers
        head_yaw = self.apply_deadzone(tracking_data.head_yaw, self.head_yaw_deadzone)
        head_pitch = self.apply_deadzone(tracking_data.head_pitch, self.head_pitch_deadzone)
        head_roll = self.apply_deadzone(tracking_data.head_roll, self.head_roll_deadzone)
        eye_left = self.apply_deadzone(tracking_data.eye_left, self.eye_left_deadzone)
        eye_right = self.apply_deadzone(tracking_data.eye_right, self.eye_right_deadzone)
        mouth_open = self.apply_deadzone(tracking_data.mouth_open, self.mouth_open_deadzone)
        mouth_wide = self.apply_deadzone(tracking_data.mouth_wide, self.mouth_wide_deadzone)

        # Map head rotations with individual axis multipliers (VTube Studio expects values in degrees)
        vts_params["ParamAngleX"] = head_yaw * 30.0 * self.head_yaw_multiplier  # Horizontal rotation
        vts_params["ParamAngleY"] = head_pitch * 30.0 * self.head_pitch_multiplier  # Vertical rotation
        vts_params["ParamAngleZ"] = head_roll * 30.0 * self.head_roll_multiplier  # Roll rotation

        # Map eye blinks with individual multipliers (VTube Studio expects 0.0 to 1.0)
        vts_params["ParamEyeLOpen"] = max(0.0, min(1.0, 1.0 - (eye_left * self.eye_left_multiplier)))
        vts_params["ParamEyeROpen"] = max(0.0, min(1.0, 1.0 - (eye_right * self.eye_right_multiplier)))

        # Map mouth parameters with multipliers (VTube Studio expects 0.0 to 1.0)
        vts_params["ParamMouthOpenY"] = max(0.0, min(1.0, mouth_open * self.mouth_open_multiplier))
        vts_params["ParamMouthForm"] = max(0.0, min(1.0, mouth_wide * self.mouth_wide_multiplier))

        # Additional mouth shaping parameters
        # These can be derived from combinations of mouth parameters
        vts_params["ParamSmile"] = max(0.0, min(1.0, mouth_wide * 1.5))  # Smile parameter based on mouth width

        return vts_params
    
    def update_sensitivity(self,
                          head_rotation_multiplier=None,
                          head_yaw_multiplier=None,
                          head_pitch_multiplier=None,
                          head_roll_multiplier=None,
                          eye_blink_multiplier=None,
                          eye_left_multiplier=None,
                          eye_right_multiplier=None,
                          mouth_open_multiplier=None,
                          mouth_wide_multiplier=None):
        """
        Update sensitivity multipliers.

        Args:
            head_rotation_multiplier: Multiplier for head rotations (legacy, applies to all axes)
            head_yaw_multiplier: Multiplier for head yaw (horizontal rotation)
            head_pitch_multiplier: Multiplier for head pitch (vertical rotation)
            head_roll_multiplier: Multiplier for head roll (tilt rotation)
            eye_blink_multiplier: Multiplier for eye blinks (legacy, applies to both eyes)
            eye_left_multiplier: Multiplier for left eye
            eye_right_multiplier: Multiplier for right eye
            mouth_open_multiplier: Multiplier for mouth opening
            mouth_wide_multiplier: Multiplier for mouth widening
        """
        if head_rotation_multiplier is not None:
            # Apply legacy multiplier to all head rotation axes
            self.head_yaw_multiplier = head_rotation_multiplier
            self.head_pitch_multiplier = head_rotation_multiplier
            self.head_roll_multiplier = head_rotation_multiplier
        else:
            # Update individual axes if specified
            if head_yaw_multiplier is not None:
                self.head_yaw_multiplier = head_yaw_multiplier
            if head_pitch_multiplier is not None:
                self.head_pitch_multiplier = head_pitch_multiplier
            if head_roll_multiplier is not None:
                self.head_roll_multiplier = head_roll_multiplier

        if eye_blink_multiplier is not None:
            # Apply legacy multiplier to both eyes
            self.eye_left_multiplier = eye_blink_multiplier
            self.eye_right_multiplier = eye_blink_multiplier
        else:
            # Update individual eyes if specified
            if eye_left_multiplier is not None:
                self.eye_left_multiplier = eye_left_multiplier
            if eye_right_multiplier is not None:
                self.eye_right_multiplier = eye_right_multiplier

        if mouth_open_multiplier is not None:
            self.mouth_open_multiplier = mouth_open_multiplier
        if mouth_wide_multiplier is not None:
            self.mouth_wide_multiplier = mouth_wide_multiplier

        logging.info(f"Sensitivity updated - "
                    f"Head Yaw: {self.head_yaw_multiplier}, "
                    f"Head Pitch: {self.head_pitch_multiplier}, "
                    f"Head Roll: {self.head_roll_multiplier}, "
                    f"Eye Left: {self.eye_left_multiplier}, "
                    f"Eye Right: {self.eye_right_multiplier}, "
                    f"Mouth Open: {self.mouth_open_multiplier}, "
                    f"Mouth Wide: {self.mouth_wide_multiplier}")

    def update_deadzones(self,
                        head_yaw_deadzone=None,
                        head_pitch_deadzone=None,
                        head_roll_deadzone=None,
                        eye_left_deadzone=None,
                        eye_right_deadzone=None,
                        mouth_open_deadzone=None,
                        mouth_wide_deadzone=None):
        """
        Update deadzone values for different parameters.

        Args:
            head_yaw_deadzone: Deadzone for head yaw
            head_pitch_deadzone: Deadzone for head pitch
            head_roll_deadzone: Deadzone for head roll
            eye_left_deadzone: Deadzone for left eye
            eye_right_deadzone: Deadzone for right eye
            mouth_open_deadzone: Deadzone for mouth open
            mouth_wide_deadzone: Deadzone for mouth wide
        """
        if head_yaw_deadzone is not None:
            self.head_yaw_deadzone = max(0.0, min(1.0, head_yaw_deadzone))
        if head_pitch_deadzone is not None:
            self.head_pitch_deadzone = max(0.0, min(1.0, head_pitch_deadzone))
        if head_roll_deadzone is not None:
            self.head_roll_deadzone = max(0.0, min(1.0, head_roll_deadzone))
        if eye_left_deadzone is not None:
            self.eye_left_deadzone = max(0.0, min(1.0, eye_left_deadzone))
        if eye_right_deadzone is not None:
            self.eye_right_deadzone = max(0.0, min(1.0, eye_right_deadzone))
        if mouth_open_deadzone is not None:
            self.mouth_open_deadzone = max(0.0, min(1.0, mouth_open_deadzone))
        if mouth_wide_deadzone is not None:
            self.mouth_wide_deadzone = max(0.0, min(1.0, mouth_wide_deadzone))

        logging.info(f"Deadzones updated - "
                    f"Head Yaw: {self.head_yaw_deadzone}, "
                    f"Head Pitch: {self.head_pitch_deadzone}, "
                    f"Head Roll: {self.head_roll_deadzone}, "
                    f"Eye Left: {self.eye_left_deadzone}, "
                    f"Eye Right: {self.eye_right_deadzone}, "
                    f"Mouth Open: {self.mouth_open_deadzone}, "
                    f"Mouth Wide: {self.mouth_wide_deadzone}")

    def normalize_value(self, value: float, min_val: float = -1.0, max_val: float = 1.0) -> float:
        """
        Normalize a value to the specified range.

        Args:
            value: Input value
            min_val: Minimum value in range
            max_val: Maximum value in range

        Returns:
            Normalized value within range
        """
        # Clamp value to range
        clamped = max(min_val, min(max_val, value))
        # Normalize to 0-1 range
        normalized = (clamped - min_val) / (max_val - min_val)
        return normalized

    def process_tracking_data(self, tracking_data: FaceTrackingData,
                            protocol: str = "both") -> dict:
        """
        Process tracking data for specified protocol(s).

        Args:
            tracking_data: Raw face tracking data
            protocol: "vmc", "vts", or "both"

        Returns:
            Dictionary containing parameters for specified protocol(s)
        """
        result = {}

        if protocol.lower() in ["vmc", "both"]:
            result["vmc"] = self.map_to_vmc_params(tracking_data)

        if protocol.lower() in ["vts", "both"]:
            result["vts"] = self.map_to_vts_params(tracking_data)

        return result

if __name__ == "__main__":
    # Test the landmarks to parameters mapping
    from .face_tracking import FaceTrackingData

    mapper = LandmarksToParameters()

    # Create test tracking data
    test_data = FaceTrackingData(
        head_yaw=0.3,
        head_pitch=0.2,
        head_roll=0.1,
        eye_left=0.8,
        eye_right=0.7,
        mouth_open=0.6,
        mouth_wide=0.5,
        face_detected=True
    )

    print("Test tracking data:")
    print(f"  Head Yaw: {test_data.head_yaw}")
    print(f"  Head Pitch: {test_data.head_pitch}")
    print(f"  Head Roll: {test_data.head_roll}")
    print(f"  Left Eye: {test_data.eye_left}")
    print(f"  Right Eye: {test_data.eye_right}")
    print(f"  Mouth Open: {test_data.mouth_open}")
    print(f"  Mouth Wide: {test_data.mouth_wide}")

    # Test VMC mapping
    vmc_params = mapper.map_to_vmc_params(test_data)
    print("\nVMC Parameters:")
    for param, value in vmc_params.items():
        print(f"  {param}: {value:.3f}")

    # Test VTS mapping
    vts_params = mapper.map_to_vts_params(test_data)
    print("\nVTS Parameters:")
    for param, value in vts_params.items():
        print(f"  {param}: {value:.3f}")