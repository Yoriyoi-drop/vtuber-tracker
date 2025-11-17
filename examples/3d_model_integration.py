#!/usr/bin/env python3
"""
Contoh integrasi VTuber Tracker dengan model 3/2D
"""
import sys
import os
import json
import math

# Tambahkan root proyek ke path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from vtuber_tracker_lib import VTuberTracker, VTuberConfig

def map_range(value, in_min, in_max, out_min, out_max):
    """Mengonversi nilai dari rentang input ke rentang output"""
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

class Model3DController:
    """
    Kelas untuk mengontrol model 3/2D berdasarkan data pelacakan wajah
    """
    def __init__(self):
        self.parameters = {
            # Rotasi kepala
            'head_y': 0.0,    # Rotasi kiri/kanan (Y)
            'head_x': 0.0,    # Rotasi atas/bawah (X)
            'head_z': 0.0,    # Rotasi miring (Z)
            
            # Ekspresi wajah
            'eye_blink_l': 0.0,   # Kedipan mata kiri
            'eye_blink_r': 0.0,   # Kedipan mata kanan
            'mouth_open': 0.0,    # Pembukaan mulut
            'mouth_form': 0.0,    # Bentuk mulut
            
            # Ekspresi tambahan
            'eye_happy': 0.0,     # Ekspresi bahagia di mata
            'cheek': 0.0,         # Kemerahan pipi
        }
    
    def update_from_tracking_data(self, face_data):
        """
        Memperbarui parameter berdasarkan data pelacakan wajah
        """
        # Konversi rotasi kepala
        self.parameters['head_y'] = map_range(face_data.head_yaw, -0.5, 0.5, -30, 30)  # Derajat
        self.parameters['head_x'] = map_range(face_data.head_pitch, -0.3, 0.3, -20, 20)  # Derajat
        self.parameters['head_z'] = map_range(face_data.head_roll, -0.3, 0.3, -15, 15)  # Derajat
        
        # Konversi ekspresi mata
        self.parameters['eye_blink_l'] = min(1.0, max(0.0, face_data.eye_left * 3.0))
        self.parameters['eye_blink_r'] = min(1.0, max(0.0, face_data.eye_right * 3.0))
        
        # Konversi ekspresi mulut
        self.parameters['mouth_open'] = min(1.0, max(0.0, face_data.mouth_open * 2.0))
        self.parameters['mouth_form'] = min(1.0, max(0.0, face_data.mouth_wide * 2.0))
        
        return self.parameters
    
    def to_live2d_format(self):
        """
        Mengonversi parameter ke format Live2D
        """
        live2d_params = {
            "angle_x": self.parameters['head_x'],
            "angle_y": self.parameters['head_y'],
            "angle_z": self.parameters['head_z'],
            "eye_l_open": 1.0 - self.parameters['eye_blink_l'],
            "eye_r_open": 1.0 - self.parameters['eye_blink_r'],
            "mouth_open_y": self.parameters['mouth_open'],
            "mouth_form": self.parameters['mouth_form'],
        }
        return live2d_params
    
    def to_json_format(self):
        """
        Mengonversi parameter ke format JSON untuk aplikasi lain
        """
        return json.dumps(self.parameters, indent=2)

def simulate_3d_model_integration():
    """
    Simulasi integrasi dengan model 3/2D
    """
    print("=== Simulasi Integrasi Model 3/2D ===")
    print("Menunjukkan bagaimana data pelacakan wajah dikonversi ke kontrol model 3D")
    
    controller = Model3DController()
    
    # Simulasi data pelacakan wajah (biasanya dari face_tracker)
    class MockFaceData:
        def __init__(self, yaw, pitch, roll, eye_left, eye_right, mouth_open, mouth_wide):
            self.head_yaw = yaw
            self.head_pitch = pitch
            self.head_roll = roll
            self.eye_left = eye_left
            self.eye_right = eye_right
            self.mouth_open = mouth_open
            self.mouth_wide = mouth_wide
    
    # Simulasi beberapa ekspresi
    test_cases = [
        ("Wajah netral", MockFaceData(0.0, 0.0, 0.0, 0.1, 0.1, 0.1, 0.1)),
        ("Putar kepala ke kanan", MockFaceData(0.3, 0.0, 0.0, 0.1, 0.1, 0.1, 0.1)),
        ("Putar kepala ke kiri", MockFaceData(-0.3, 0.0, 0.0, 0.1, 0.1, 0.1, 0.1)),
        ("Kedipan mata", MockFaceData(0.0, 0.0, 0.0, 0.4, 0.4, 0.1, 0.1)),
        ("Buka mulut", MockFaceData(0.0, 0.0, 0.0, 0.1, 0.1, 0.4, 0.1)),
    ]
    
    for name, face_data in test_cases:
        print(f"\n{name}:")
        params = controller.update_from_tracking_data(face_data)
        live2d_format = controller.to_live2d_format()
        
        print(f"  Parameter: {params}")
        print(f"  Format Live2D: {live2d_format}")

def setup_3d_model_config():
    """
    Pengaturan untuk integrasi model 3D
    """
    print("\n=== Pengaturan Integrasi Model 3/2D ===")
    print("\nUntuk menghubungkan VTuber Tracker ke model 3/2D:")
    print("\n1. Live2D Cubism:")
    print("   - Gunakan Live2D Cubism SDK")
    print("   - Kirim parameter melalui OSC ke Live2D")
    print("   - Format parameter: angle_x, angle_y, angle_z, eye_l_open, dll")
    
    print("\n2. VRM (3D Model):")
    print("   - Gunakan model VRM dalam Blender/VRoid Studio")
    print("   - Kirim parameter melalui OSC ke aplikasi 3D (VRM Viewer)")
    print("   - Cocok untuk integrasi VSeeFace atau VTube Studio")
    
    print("\n3. Spine 2D:")
    print("   - Gunakan Spine untuk skeleton 2D")
    print("   - Kirim parameter sebagai kontrol bone")
    print("   - Efisien dan fleksibel untuk animasi 2D")
    
    print("\n4. Custom OpenGL/Unity:")
    print("   - Bangun renderer sendiri")
    print("   - Gunakan parameter sebagai transformasi")
    print("   - Kontrol penuh atas tampilan dan efek")

def live2d_osc_mapping_example():
    """
    Contoh mapping parameter ke OSC untuk Live2D
    """
    print("\n=== Contoh Mapping OSC untuk Live2D ===")
    
    # Parameter yang biasanya digunakan di Live2D
    osc_mapping = {
        "/Live2D/angle/x": "head_x",      # Rotasi horizontal kepala
        "/Live2D/angle/y": "head_y",      # Rotasi vertikal kepala
        "/Live2D/angle/z": "head_z",      # Rotasi miring kepala
        "/Live2D/eye/l/open": "eye_l_open",  # Pembukaan mata kiri
        "/Live2D/eye/r/open": "eye_r_open",  # Pembukaan mata kanan
        "/Live2D/mouth/open": "mouth_open_y",  # Pembukaan mulut
        "/Live2D/mouth/form": "mouth_form",   # Bentuk mulut
    }
    
    print("Mapping OSC parameter untuk Live2D:")
    for osc_address, param_name in osc_mapping.items():
        print(f"  {osc_address} -> {param_name}")

def vrm_integration_example():
    """
    Contoh integrasi dengan VRM (model 3D)
    """
    print("\n=== Contoh Integrasi VRM (Model 3D) ===")
    
    vrm_blendshapes = {
        "A": "mouth_open",      # Pembukaan mulut
        "I": "mouth_form",      # Bentuk mulut "i"
        "U": "mouth_form",      # Bentuk mulut "u"
        "E": "mouth_form",      # Bentuk mulut "e"
        "O": "mouth_open",      # Bentuk mulut "o"
        "Blink": "eye_blink_l", # Kedipan mata kiri
        "BlinkLeft": "eye_blink_l",   # Kedipan mata kiri
        "BlinkRight": "eye_blink_r",  # Kedipan mata kanan
        "LookUp": "head_x",     # Posisi mata ke atas
        "LookDown": "head_x",   # Posisi mata ke bawah
        "LookLeft": "head_y",   # Posisi mata ke kiri
        "LookRight": "head_y",  # Posisi mata ke kanan
    }
    
    print("Mapping blendshape untuk VRM:")
    for blendshape, param_name in vrm_blendshapes.items():
        print(f"  {blendshape} <- {param_name}")

if __name__ == "__main__":
    print("VTuber Tracker - Integrasi Model 3/2D")
    print("=" * 50)
    
    print("\nModel 3/2D menggabungkan sprite 2D dengan animasi 3D.")
    print("VTuber Tracker saat ini menghasilkan parameter pelacakan wajah")
    print("yang dapat dikonversi ke kontrol model 3/2D.")
    
    simulate_3d_model_integration()
    setup_3d_model_config()
    live2d_osc_mapping_example()
    vrm_integration_example()
    
    print("\nCatatan:")
    print("- VTuber Tracker saat ini menghasilkan parameter pelacakan")
    print("- Parameter ini perlu dikonversi ke format yang dimengerti model 3D/2D")
    print("- Bisa menggunakan Live2D, Spine, VRM, atau sistem kustom")
    print("- Umumnya dikirim melalui protokol OSC atau WebSocket")