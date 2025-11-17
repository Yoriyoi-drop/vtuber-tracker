#!/usr/bin/env python3
"""
Contoh penggunaan kalibrasi VTuber Tracker
"""
import sys
import os
import time

# Tambahkan root proyek ke path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from vtuber_tracker_lib import VTuberTracker, VTuberConfig

def main():
    """
    Contoh demonstrasi kalibrasi
    """
    print("VTuber Tracker - Contoh Kalibrasi")
    print("=" * 40)
    
    # Buat konfigurasi
    config = VTuberConfig(
        camera_index=0,
        frame_width=640,
        frame_height=480,
        smoothing_alpha=0.3,
        enable_virtual_camera=False,
        enable_vmc_output=True,
        vmc_host="127.0.0.1",
        vmc_port=39539
    )
    
    tracker = VTuberTracker(config)
    
    print("Memulai pelacakan...")
    tracker.start()
    
    print("\nLangkah-langkah kalibrasi:")
    print("1. Pastikan wajah Anda terlihat jelas di kamera")
    print("2. Jaga posisi wajah tetap netral (mata lurus ke kamera, mulut tertutup)")
    print("3. Tekan Enter untuk memulai proses kalibrasi")
    
    input("\nTekan Enter ketika siap untuk kalibrasi...")
    
    print("Memulai kalibrasi...")
    tracker.start_calibration()
    
    # Tunggu beberapa detik untuk kalibrasi
    calibration_time = 5
    for i in range(calibration_time, 0, -1):
        print(f"Kalibrasi dalam {i} detik...")
        time.sleep(1)
    
    # Tunggu hasil kalibrasi
    time.sleep(2)
    
    if tracker.is_calibrated():
        print("✓ Kalibrasi berhasil!")
        print("Sekarang posisi netral Anda telah disimpan.")
        print("Gerakan wajah akan dihitung relatif terhadap posisi ini.")
    else:
        print("✗ Kalibrasi gagal. Pastikan wajah terdeteksi dengan baik.")
    
    print("\nMencoba mode presisi...")
    tracker.enable_precision_mode(enabled=True, multiplier=1.2)
    print("Mode presisi diaktifkan - gerakan halus akan diperkuat")
    
    print("\nTekan Ctrl+C untuk berhenti")
    
    try:
        # Jalankan dengan kalibrasi
        start_time = time.time()
        while True:
            time.sleep(1)
            if time.time() - start_time > 30:  # Jika lebih dari 30 detik, tanyakan
                response = input("Lanjutkan pelacakan? (y/n): ")
                if response.lower() not in ['y', 'yes']:
                    break
                start_time = time.time()
    except KeyboardInterrupt:
        print("\nBerhenti oleh pengguna")
    
    print("Menghentikan tracker...")
    tracker.stop()
    print("Selesai!")

def sensitivity_tuning_example():
    """
    Contoh penyesuaian sensitivitas
    """
    print("\nVTuber Tracker - Contoh Penyesuaian Sensitivitas")
    print("=" * 50)
    
    # Konfigurasi dengan sensitivitas khusus
    config = VTuberConfig(
        camera_index=0,
        frame_width=640,
        frame_height=480,
        smoothing_alpha=0.25,
        enable_virtual_camera=False,
        enable_vmc_output=True,
        vmc_host="127.0.0.1",
        vmc_port=39539,
        # Sensitivitas yang berbeda untuk setiap parameter
        head_yaw_multiplier=1.0,
        head_pitch_multiplier=0.8,  # Kurangi sensitivitas pitch
        head_roll_multiplier=1.2,   # Tambah sensitivitas roll
        eye_left_multiplier=2.0,    # Sangat sensitif untuk mata kiri
        eye_right_multiplier=2.0,   # Sangat sensitif untuk mata kanan
        mouth_open_multiplier=1.5,  # Tambah sensitivitas mulut
        mouth_wide_multiplier=1.3   # Tambah sensitivitas lebar mulut
    )
    
    tracker = VTuberTracker(config)
    
    print("Memulai pelacakan dengan sensitivitas khusus...")
    tracker.start()
    
    print("Sensitivitas yang diatur:")
    print("- Rotasi kepala (yaw): normal")
    print("- Rotasi kepala (pitch): dikurangi")
    print("- Rotasi kepala (roll): ditingkatkan")
    print("- Gerakan mata: sangat responsif")
    print("- Gerakan mulut: lebih responsif")
    
    print("\nTekan Ctrl+C untuk berhenti")
    
    try:
        start_time = time.time()
        while time.time() - start_time < 45:
            time.sleep(0.5)
            print(".", end="", flush=True)
    except KeyboardInterrupt:
        print("\nBerhenti oleh pengguna")
    
    tracker.stop()
    print("\nSelesai!")

if __name__ == "__main__":
    main()
    
    response = input("\nJalankan contoh penyesuaian sensitivitas? (y/n): ")
    if response.lower() in ['y', 'yes']:
        sensitivity_tuning_example()