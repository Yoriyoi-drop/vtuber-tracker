#!/usr/bin/env python3
"""
Contoh integrasi VTuber Tracker dengan semua platform streaming
"""
import sys
import os
import time

# Tambahkan root proyek ke path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from vtuber_tracker_lib import VTuberTracker, VTuberConfig

def streaming_platforms_overview():
    """
    Gambaran umum dukungan platform streaming
    """
    platforms = {
        "VSeeFace": {
            "protocol": "VMC (Virtual Motion Capture)",
            "port": 39539,
            "method": "OSC direct connection",
            "use_case": "Core tracker, converts to virtual camera",
            "model_support": ["Live2D", "VRM", "3D"]
        },
        "OBS Studio": {
            "protocol": "Virtual Camera Plugin / NDI / DShow",
            "port": "N/A",
            "method": "VSeeFace camera output",
            "use_case": "Streaming to multiple platforms",
            "model_support": ["VSeeFace models"]
        },
        "Twitch": {
            "protocol": "RTMP / OBS output",
            "port": "N/A",
            "method": "OBS -> Twitch",
            "use_case": "Live streaming",
            "model_support": ["VSeeFace models via OBS"]
        },
        "YouTube Live": {
            "protocol": "RTMPS / OBS output",
            "port": "N/A",
            "method": "OBS -> YouTube",
            "use_case": "Broadcasting",
            "model_support": ["VSeeFace models via OBS"]
        },
        "Zoom": {
            "protocol": "DirectShow / Virtual Camera",
            "port": "N/A",
            "method": "VSeeFace virtual camera",
            "use_case": "Meetings / Calls",
            "model_support": ["VSeeFace models"]
        },
        "Discord": {
            "protocol": "DirectShow / Virtual Camera",
            "port": "N/A",
            "method": "VSeeFace virtual camera",
            "use_case": "Voice/Video calls",
            "model_support": ["VSeeFace models"]
        },
        "VRChat": {
            "protocol": "Camera input",
            "port": "N/A",
            "method": "VSeeFace virtual camera",
            "use_case": "Virtual reality social platform",
            "model_support": ["VSeeFace models"]
        },
        "Facebook Live": {
            "protocol": "RTMPS / OBS output",
            "port": "N/A",
            "method": "OBS -> Facebook",
            "use_case": "Social media broadcasting",
            "model_support": ["VSeeFace models via OBS"]
        }
    }
    
    print("=== dukungan Platform Streaming VTuber Tracker ===")
    print("VTuber Tracker dapat digunakan di semua platform streaming utama!\n")
    
    for platform, info in platforms.items():
        print(f"{platform}:")
        print(f"  - Protocol: {info['protocol']}")
        print(f"  - Communication: {info['method']}")
        print(f"  - Use Case: {info['use_case']}")
        print(f"  - Model Support: {', '.join(info['model_support'])}")
        print()

def setup_for_all_platforms():
    """
    Panduan setup untuk semua platform
    """
    print("=== Panduan Setup untuk Semua Platform Streaming ===")
    
    print("\n1. Setup Inti (Untuk semua platform):")
    print("   - Pastikan VTuber Tracker berjalan dengan baik")
    print("   - Siapkan model VTuber (Live2D/VRM)")
    print("   - Install VSeeFace sebagai penghubung")
    
    print("\n2. Flow Data Umum:")
    print("   VTuber Tracker → VSeeFace → Platform Target")
    print("   (Pelacakan wajah) → (Model 3D/2D) → (Output platform)")
    
    print("\n3. Per Platform:")
    
    platforms_steps = {
        "OBS Studio": [
            "Install OBS Virtual Camera Plugin",
            "Pilih VSeeFace sebagai input kamera",
            "Gunakan OBS untuk stream ke berbagai platform"
        ],
        "Twitch & YouTube": [
            "Gunakan OBS Studio dengan VSeeFace sebagai sumber",
            "Atur stream key dari platform target",
            "Stream dengan model VTuber Anda"
        ],
        "Zoom & Discord": [
            "Pilih VSeeFace sebagai kamera video",
            "Wajah Anda otomatis menjadi model VTuber"
        ],
        "VRChat": [
            "Install VRCFaceTracking (jika ingin presisi tinggi)",
            "Atau gunakan VSeeFace kamera virtual",
            "Pilih model yang kompatibel dengan VRChat"
        ],
        "Facebook Live": [
            "Gunakan OBS Studio sebagai intermediate",
            "Atur stream ke Facebook Live"
        ]
    }
    
    for platform, steps in platforms_steps.items():
        print(f"\n   {platform}:")
        for i, step in enumerate(steps, 1):
            print(f"   {i}. {step}")

def create_universal_streamer():
    """
    Contoh konfigurasi untuk semua platform
    """
    print("\n=== Konfigurasi Universal VTuber ===")
    
    # Konfigurasi ini bisa digunakan untuk semua platform
    config = VTuberTracker(
        VTuberConfig(
            frame_width=640,
            frame_height=480,
            smoothing_alpha=0.25,  # Balance antara responsivitas dan kehalusan
            enable_vmc_output=True,  # Untuk VSeeFace
            vmc_host="127.0.0.1",
            vmc_port=39539,  # Port VSeeFace
        )
    )
    
    print("Konfigurasi universal dibuat:")
    print("- Resolusi 640x480 (optimal untuk streaming)")
    print("- Smoothing 0.25 (seimbang)")
    print("- Output VMC aktif (untuk VSeeFace)")
    print("- Port 39539 (default VSeeFace)")
    
    return config

def test_all_platforms():
    """
    Simulasi penggunaan di semua platform
    """
    print("\n=== Simulasi Penggunaan di Semua Platform ===")
    
    platforms = [
        {"name": "VSeeFace", "time": 5},
        {"name": "OBS Studio", "time": 5},
        {"name": "Zoom Meeting", "time": 5},
        {"name": "Twitch Stream", "time": 10},
        {"name": "VRChat Social", "time": 10},
        {"name": "YouTube Live", "time": 10}
    ]
    
    print("VTuber sedang aktif di berbagai platform...")
    
    for platform in platforms:
        print(f"\n🎮 {platform['name']} (aktif {platform['time']} detik)")
        
        # Simulasi aktivitas
        for i in range(platform['time'], 0, -1):
            print(f"   [Tersambung] Hitung mundur: {i}s", end="\r")
            time.sleep(1)
        print(f"   ✓ {platform['name']} selesai            ")  # extra spaces to clear the line

def advanced_configurations():
    """
    Konfigurasi lanjutan untuk platform spesifik
    """
    print("\n=== Konfigurasi Lanjutan per Platform ===")
    
    configs = {
        "Streaming (Twitch/YouTube)": {
            "frame_width": 1280,
            "frame_height": 720,
            "smoothing_alpha": 0.2,
            "notes": "Resolusi tinggi untuk kualitas streaming"
        },
        "Meeting (Zoom/Discord)": {
            "frame_width": 640,
            "frame_height": 480,
            "smoothing_alpha": 0.3,
            "notes": "Optimal untuk meeting, lebih smooth"
        },
        "Game (VRChat)": {
            "frame_width": 640,
            "frame_height": 480,
            "smoothing_alpha": 0.15,
            "notes": "Responsif untuk interaksi real-time"
        },
        "Recording": {
            "frame_width": 1920,
            "frame_height": 1080,
            "smoothing_alpha": 0.1,
            "notes": "Resolusi tinggi untuk rekaman"
        }
    }
    
    for platform, config in configs.items():
        print(f"\n{platform}:")
        for key, value in config.items():
            if key != "notes":
                print(f"  - {key}: {value}")
        print(f"  - Catatan: {config['notes']}")

if __name__ == "__main__":
    print("VTuber Tracker - Dukungan Semua Platform Streaming")
    print("=" * 55)
    
    streaming_platforms_overview()
    setup_for_all_platforms()
    create_universal_streamer()
    test_all_platforms()
    advanced_configurations()
    
    print("\n" + "="*55)
    print("✅ VTuber Tracker siap digunakan di semua platform!")
    print("   - Game (Steam, VRChat, dll)")
    print("   - Live Stream (Twitch, YouTube, Facebook)")
    print("   - Meeting (Zoom, Discord, Teams)")
    print("   - Broadcasting dan lainnya")
    print("="*55)