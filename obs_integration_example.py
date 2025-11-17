"""
Contoh penggunaan VTuber Tracker dengan OBS Virtual Camera
"""

from vtuber_tracker_lib import VTuberTracker, VTuberConfig
import time
import sys

def find_obs_virtual_camera():
    """Coba deteksi OBS Virtual Camera"""
    import cv2
    
    # Coba nama-nama umum OBS Virtual Camera
    obs_names = [
        "OBS Virtual Camera",
        "obs-virtual-source"  # Nama di Linux
    ]
    
    # Di Linux, biasanya virtual camera ada di indeks yang lebih tinggi
    # Di Windows/Mac, mungkin muncul dengan nama tertentu
    import subprocess
    try:
        result = subprocess.run(['v4l2-ctl', '--list-devices'], 
                              capture_output=True, text=True)
        if 'obs' in result.stdout.lower() or 'virtual' in result.stdout.lower():
            # Temukan indeks dari output
            lines = result.stdout.split('\n')
            # Pencarian lebih lanjut bisa ditambahkan di sini
            return True
    except:
        pass  # v4l2-ctl mungkin tidak tersedia
    
    # Sebagai fallback, coba beberapa indeks tinggi
    # karena virtual camera sering di indeks tinggi
    for i in range(5, 10):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                cap.release()
                return i  # Kembalikan indeks virtual camera jika ditemukan
        cap.release()
    
    return None

def main():
    print("VTuber Tracker - Contoh Penggunaan dengan OBS Virtual Camera")
    print("=" * 60)
    
    print("Mencari OBS Virtual Camera...")
    obs_cam_index = find_obs_virtual_camera()
    
    if obs_cam_index is not None:
        print(f"✅ OBS Virtual Camera ditemukan di indeks: {obs_cam_index}")
        camera_index = obs_cam_index
    else:
        print("⚠️  OBS Virtual Camera tidak ditemukan")
        print("Pastikan OBS sedang berjalan dan Virtual Camera sudah diaktifkan")
        print("Coba cari kamera biasa...")
        
        # Gunakan utility untuk mencari kamera biasa
        from camera_util import detect_cameras
        available_cams = detect_cameras()
        if not available_cams:
            print("❌ Tidak ada kamera yang ditemukan. Pastikan:")
            print("   1. OBS Virtual Camera diaktifkan (Tools > Virtual Camera)")
            print("   2. Kamera fisik terhubung dan tidak digunakan aplikasi lain")
            return
        camera_index = available_cams[0]['index']
    
    # Buat konfigurasi dengan kamera yang ditemukan
    config = VTuberConfig(
        camera_index=camera_index,
        frame_width=640,
        frame_height=480,
        smoothing_alpha=0.2,
        enable_smoothing=True,
        enable_virtual_camera=False,  # Kita tidak perlu virtual camera output
        enable_vmc_output=True,       # Tapi tetap kirim ke VMC
        vmc_host="127.0.0.1",
        vmc_port=39539
    )
    
    print(f"\nMenggunakan kamera indeks: {camera_index}")
    print("Memulai VTuber Tracker...")
    
    try:
        tracker = VTuberTracker(config)
        tracker.start()
        
        print("✅ VTuber Tracker berjalan!")
        print("Pastikan VSeeFace atau perangkat lunak VMC lain juga berjalan.")
        print("Tekan Ctrl+C untuk berhenti.")
        
        # Jalankan selama 30 detik sebagai contoh
        time.sleep(30)
        
    except KeyboardInterrupt:
        print("\nMenghentikan pelacakan...")
    
    finally:
        tracker.stop()
        print("Pelacakan dihentikan.")

if __name__ == "__main__":
    main()