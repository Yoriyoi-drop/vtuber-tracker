#!/usr/bin/env python3
"""
Contoh penggunaan sederhana VTuber Tracker
"""
import sys
import os
import time
import logging

# Tambahkan root proyek ke path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from vtuber_tracker_lib import VTuberTracker, VTuberConfig

def main():
    """
    Contoh penggunaan dasar VTuber Tracker
    """
    print("VTuber Tracker - Contoh Penggunaan")
    print("=" * 40)
    
    # Buat konfigurasi
    config = VTuberConfig(
        camera_index=0,
        frame_width=640,
        frame_height=480,
        smoothing_alpha=0.3,
        enable_virtual_camera=False,  # Set ke True jika ingin output ke kamera virtual
        enable_vmc_output=True,
        vmc_host="127.0.0.1",
        vmc_port=39539
    )
    
    print("Membuat tracker...")
    tracker = VTuberTracker(config)
    
    print("Memulai pelacakan...")
    tracker.start()
    
    print("\nInstruksi:")
    print("- Tekan kalibrasi saat wajah Anda dalam posisi netral")
    print("- Gunakan GUI untuk mengatur sensitivitas")
    print("- Tekan Ctrl+C untuk berhenti")
    
    try:
        # Jalankan selama 30 detik atau sampai dihentikan
        start_time = time.time()
        while time.time() - start_time < 30:
            time.sleep(1)
            print(".", end="", flush=True)
    except KeyboardInterrupt:
        print("\nBerhenti oleh pengguna")
    
    print("\nMenghentikan tracker...")
    tracker.stop()
    print("Selesai!")

def advanced_example():
    """
    Contoh penggunaan lanjutan dengan pengaturan kustom
    """
    print("\nVTuber Tracker - Contoh Penggunaan Lanjutan")
    print("=" * 50)
    
    # Konfigurasi lanjutan
    config = VTuberConfig(
        camera_index=0,
        frame_width=1280,
        frame_height=720,
        smoothing_alpha=0.2,  # Lebih smooth
        enable_smoothing=True,
        enable_virtual_camera=False,
        enable_vmc_output=True,
        vmc_host="127.0.0.1",
        vmc_port=39539,
        # Kalibrasi sensitivitas lanjutan
        head_yaw_multiplier=1.2,
        head_pitch_multiplier=1.0,
        head_roll_multiplier=1.0,
        eye_left_multiplier=1.5,  # Lebih sensitif untuk gerakan mata
        eye_right_multiplier=1.5,
        mouth_open_multiplier=1.3,
        mouth_wide_multiplier=1.2
    )
    
    tracker = VTuberTracker(config)
    
    print("Memulai pelacakan dengan konfigurasi lanjutan...")
    tracker.start()
    
    print("Menunggu kalibrasi...")
    time.sleep(3)
    
    # Aktifkan mode presisi
    tracker.enable_precision_mode(enabled=True, multiplier=1.5)
    print("Mode presisi diaktifkan")
    
    try:
        # Jalankan selama 60 detik
        start_time = time.time()
        while time.time() - start_time < 60:
            time.sleep(1)
            print(".", end="", flush=True)
    except KeyboardInterrupt:
        print("\nBerhenti oleh pengguna")
    
    tracker.stop()
    print("Selesai!")

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Jalankan contoh dasar
    main()
    
    # Tanyakan apakah ingin menjalankan contoh lanjutan
    response = input("\nJalankan contoh lanjutan? (y/n): ")
    if response.lower() in ['y', 'yes']:
        advanced_example()