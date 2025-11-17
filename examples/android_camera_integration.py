#!/usr/bin/env python3
"""
Contoh penggunaan VTuber Tracker dengan kamera Android melalui IP Webcam
"""
import sys
import os
import time

# Tambahkan root proyek ke path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from vtuber_tracker_lib import VTuberTracker, VTuberConfig

def setup_android_camera_stream():
    """
    Setup untuk menggunakan kamera Android melalui IP Webcam
    """
    print("=== Setup Kamera Android untuk VTuber Tracker ===")
    print("\nLangkah-langkah sebelum memulai:")
    print("1. Pastikan ponsel Android dan komputer terhubung ke jaringan Wi-Fi yang sama")
    print("2. Install aplikasi 'IP Webcam' di ponsel (atau aplikasi serupa)")
    print("3. Buka aplikasi IP Webcam dan tekan 'Start Server'")
    print("4. Catat alamat IP yang ditampilkan di aplikasi (misal: 192.168.1.100:8080)")
    
    print("\nFormat URL stream umum:")
    print("- HTTP: http://[IP]:[PORT]/video (contoh: http://192.168.1.100:8080/video)")
    print("- MJPEG: http://[IP]:[PORT]/mjpegad (tergantung aplikasi)")
    
    ip_address = input("\nMasukkan IP dan port kamera Android (contoh: 192.168.1.100:8080): ").strip()
    if not ip_address:
        print("IP tidak valid. Menggunakan contoh...")
        ip_address = "192.168.1.100:8080"
    
    # Bangun URL stream
    if not ip_address.startswith(('http://', 'https://')):
        stream_url = f"http://{ip_address}/video"
    else:
        # Jika sudah berisi protokol, hanya tambahkan /video jika tidak ada
        if not ip_address.endswith(('/video', '/mjpeg', '/mjpegad')):
            stream_url = f"{ip_address}/video"
        else:
            stream_url = ip_address

    return stream_url

def test_android_camera_stream(stream_url):
    """
    Uji koneksi ke kamera Android sebelum mulai tracking
    """
    print(f"\nMenguji koneksi ke: {stream_url}")
    
    try:
        import cv2
        cap = cv2.VideoCapture(stream_url)
        
        if not cap.isOpened():
            print(f"Gagal menghubung ke: {stream_url}")
            return False
            
        # Ambil beberapa frame untuk tes
        for i in range(5):
            ret, frame = cap.read()
            if ret:
                height, width = frame.shape[:2]
                print(f"✓ Frame {i+1} diterima - Resolusi: {width}x{height}")
                break
            else:
                time.sleep(0.5)
        
        cap.release()
        print("✓ Tes koneksi berhasil!")
        return True
    except Exception as e:
        print(f"✗ Error saat tes koneksi: {e}")
        return False

def run_android_vtuber_tracker():
    """
    Jalankan VTuber Tracker dengan kamera Android
    """
    print("=== Menjalankan VTuber Tracker dengan Kamera Android ===")
    
    # Setup URL stream
    stream_url = setup_android_camera_stream()
    
    # Tes koneksi
    if not test_android_camera_stream(stream_url):
        print("Gagal terhubung ke kamera Android. Pastikan:")
        print("- Ponsel dan komputer di jaringan yang sama")
        print("- IP Webcam aktif di ponsel")
        print("- Alamat IP benar")
        return False
    
    print(f"\nPersiapan selesai! Menggunakan stream: {stream_url}")
    
    # Buat konfigurasi dengan stream_url
    config = VTuberConfig(
        camera_index=0,  # Tidak digunakan saat stream_url diatur
        frame_width=640,
        frame_height=480,
        smoothing_alpha=0.3,
        enable_virtual_camera=False,  # Set ke True jika ingin output ke kamera virtual
        enable_vmc_output=True,
        vmc_host="127.0.0.1",
        vmc_port=39539,
        stream_url=stream_url  # Ini adalah kunci untuk menggunakan kamera Android
    )
    
    print("\nMembuat dan menjalankan tracker...")
    tracker = VTuberTracker(config)
    
    print("Tracker dimulai dengan kamera Android!")
    print("\nInstruksi:")
    print("- Hadapkan wajah Anda ke kamera ponsel")
    print("- Lakukan kalibrasi saat wajah dalam posisi netral")
    print("- Gunakan GUI untuk mengatur sensitivitas")
    print("- Tekan Ctrl+C untuk berhenti")
    
    try:
        tracker.start()
        
        # Jalankan selama 60 detik atau sampai dihentikan
        start_time = time.time()
        print("\nTracker aktif... ")
        
        while True:
            # Tampilkan status setiap 10 detik
            elapsed_time = time.time() - start_time
            if int(elapsed_time) % 10 == 0 and int(elapsed_time) > 0:
                print(f"[{int(elapsed_time)}s] Tracker masih berjalan...")
            
            time.sleep(1)
            
            # Batasi waktu jika tidak dihentikan manual (opsional)
            if elapsed_time > 300:  # 5 menit
                response = input(f"\nTracker telah berjalan selama {int(elapsed_time)} detik. Lanjutkan? (y/n): ")
                if response.lower() in ['n', 'no']:
                    break
                start_time = time.time()  # Reset timer
                
    except KeyboardInterrupt:
        print("\n\nMenghentikan tracker...")
    finally:
        tracker.stop()
        print("Tracker dihentikan.")
    
    return True

def show_android_camera_options():
    """
    Tampilkan opsi dan tips untuk kamera Android
    """
    print("\n=== Tips Menggunakan Kamera Android ===")
    print("\nAplikasi IP Webcam Rekomendasi:")
    print("- IP Webcam (Android) - Gratis, fitur lengkap")
    print("- CameraFi (Android) - Banyak opsi streaming")
    print("- Iriun webcam - Bisa digunakan sebagai webcam biasa")
    
    print("\nTips untuk kualitas terbaik:")
    print("- Gunakan jaringan Wi-Fi 5GHz jika tersedia")
    print("- Letakkan ponsel di tempat stabil (gunakan tripod)")
    print("- Pastikan pencahayaan cukup baik")
    print("- Atur resolusi di IP Webcam (720p biasanya optimal)")
    print("- Kurangi bitrate jika mengalami lag")
    print("- Gunakan mode Landscape di ponsel")
    
    print("\nTroubleshooting umum:")
    print("- Pastikan firewall tidak memblokir koneksi")
    print("- Uji URL di browser untuk memastikan stream aktif")
    print("- Coba ping IP ponsel untuk tes konektivitas")
    print("- Restart IP Webcam jika koneksi terputus")

if __name__ == "__main__":
    print("VTuber Tracker - Integrasi Kamera Android")
    print("=" * 50)
    
    # Tampilkan tips
    show_android_camera_options()
    
    # Tanyakan apakah ingin lanjut
    response = input("\nLanjutkan ke setup kamera Android? (y/n): ")
    if response.lower() in ['y', 'yes']:
        run_android_vtuber_tracker()
    else:
        print("Setup dibatalkan.")

    print("\nTerima kasih telah menggunakan VTuber Tracker!")