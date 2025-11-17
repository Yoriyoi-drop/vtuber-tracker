"""
Contoh penggunaan library VTuber Tracker untuk teman Anda.

Cara gunakan:
1. Pastikan semua dependensi terinstal: pip install -r requirements.txt
2. Jalankan file ini: python example_usage.py
3. Library akan mulai melacak wajah dan mengirim data ke VSeeFace
"""

from vtuber_tracker_lib import VTuberTracker, VTuberConfig
import time
import signal
import sys


def main():
    print("VTuber Tracker - Contoh Penggunaan Sederhana")
    print("=" * 50)
    
    # Buat konfigurasi dasar
    config = VTuberConfig(
        camera_index=0,                    # Gunakan kamera pertama
        frame_width=640,                   # Resolusi kamera
        frame_height=480,
        smoothing_alpha=0.2,               # Level smoothing sedang
        enable_smoothing=True,
        enable_virtual_camera=False,       # Nonaktifkan virtual camera untuk contoh ini
        enable_vmc_output=True,            # Aktifkan output ke VMC (VSeeFace)
        vmc_host="127.0.0.1",              # Host VSeeFace
        vmc_port=39539                     # Port VSeeFace
    )
    
    # Buat instance tracker
    tracker = VTuberTracker(config)
    
    print("Mempersiapkan pelacakan wajah...")
    print("Pastikan VSeeFace atau perangkat lunak VMC lain sedang berjalan.")
    print("Tekan Ctrl+C untuk berhenti.")
    print()
    
    try:
        # Mulai pelacakan
        tracker.start()
        print("Pelacakan wajah dimulai!")
        print("Silakan hadapkan wajah Anda ke kamera.")
        print()
        
        # Tunggu beberapa detik untuk melihat hasil
        running_time = 0
        while running_time < 60:  # Jalankan selama 60 detik sebagai contoh
            time.sleep(1)
            running_time += 1
            if running_time % 10 == 0:
                print(f"Telah berjalan selama {running_time} detik...")
    
    except KeyboardInterrupt:
        print("\nMenghentikan pelacakan...")
    
    finally:
        # Selalu berhenti secara benar
        tracker.stop()
        print("Pelacakan wajah dihentikan.")
        print("Terima kasih telah menggunakan VTuber Tracker!")


def signal_handler(sig, frame):
    """Handler untuk sinyal interupsi (Ctrl+C)"""
    print('\n\nMenghentikan pelacakan secara aman...')
    # Karena kita tidak punya akses ke tracker di sini, kita hanya keluar
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main()