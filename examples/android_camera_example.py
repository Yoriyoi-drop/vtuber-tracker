#!/usr/bin/env python3
"""
Contoh penggunaan VTuber Tracker dengan kamera Android melalui IP Webcam
"""
import sys
import os
import cv2
import time

# Tambahkan root proyek ke path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def setup_android_camera(ip_address="192.168.1.100", port=8080):
    """
    Setup kamera Android melalui IP Webcam
    
    Args:
        ip_address (str): Alamat IP ponsel Android Anda
        port (int): Port yang digunakan oleh IP Webcam (default: 8080)
    
    Returns:
        cv2.VideoCapture: Object kamera yang siap digunakan
    """
    # URL untuk stream video dari IP Webcam
    # Format umum: http://[IP]:[PORT]/video
    url = f"http://{ip_address}:{port}/video"
    
    print(f"Menghubungkan ke kamera Android di: {url}")
    
    # Buat VideoCapture object dengan URL stream
    cap = cv2.VideoCapture(url)
    
    # Setel beberapa parameter untuk optimasi
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Kurangi buffer untuk latensi lebih rendah
    
    # Cek apakah koneksi berhasil
    if not cap.isOpened():
        print(f"Gagal terhubung ke kamera Android di {url}")
        return None
    
    print("Koneksi ke kamera Android berhasil!")
    return cap

def test_android_camera_connection():
    """
    Fungsi untuk menguji koneksi ke kamera Android
    """
    print("=== Uji Koneksi Kamera Android ===")
    print("Pastikan:")
    print("1. Ponsel Android dan komputer terhubung ke jaringan yang sama")
    print("2. Aplikasi IP Webcam sudah berjalan di ponsel")
    print("3. Anda telah mencatat alamat IP ponsel")
    
    # Masukkan IP ponsel Anda
    ip_ponsel = input("Masukkan IP ponsel (contoh: 192.168.1.100): ").strip()
    if not ip_ponsel:
        ip_ponsel = "192.168.1.100"  # Default IP
    
    # Setup kamera
    cap = setup_android_camera(ip_ponsel, 8080)
    
    if cap is None:
        print("Tidak dapat terhubung ke kamera Android")
        return False
    
    print("Menampilkan feed kamera Android. Tekan 'q' untuk keluar.")
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("Gagal menerima frame dari kamera Android")
                break
            
            # Tampilkan frame
            cv2.imshow('Kamera Android - IP Webcam', frame)
            
            # Tekan 'q' untuk keluar
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\nDihentikan oleh pengguna")
    finally:
        cap.release()
        cv2.destroyAllWindows()
    
    return True

def integrate_with_vtuber_tracker(ip_address, port=8080):
    """
    Contoh cara mengintegrasikan dengan VTuber Tracker
    """
    print(f"\nMengintegrasikan kamera Android ({ip_address}:{port}) ke VTuber Tracker...")
    
    # In the actual implementation, you would modify the CameraCapture class
    # to accept a URL parameter instead of just camera index
    print("Catatan: Untuk integrasi penuh, Anda perlu memodifikasi CameraCapture class")
    print("di tracker/camera.py untuk mendukung stream URL dari IP Webcam")
    
    # Ini adalah contoh konsep modifikasi yang diperlukan:
    print("""
Konsep perubahan untuk tracker/camera.py:

class CameraCapture:
    def __init__(self, camera_index=0, frame_width=640, frame_height=480, stream_url=None):
        self.frame_width = frame_width
        self.frame_height = frame_height
        
        if stream_url:
            # Gunakan stream URL dari IP Webcam
            self.cap = cv2.VideoCapture(stream_url)
        else:
            # Gunakan kamera lokal biasa
            self.cap = cv2.VideoCapture(camera_index)
        
        # Setel parameter kamera
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

def get_frame(self):
    ret, frame = self.cap.read()
    if ret:
        return frame
    return None
    """)

if __name__ == "__main__":
    print("VTuber Tracker - Panduan Menggunakan Kamera Android")
    print("=" * 50)
    
    print("\n1. Pengaturan Kamera Android:")
    print("   - Install 'IP Webcam' di ponsel Android")
    print("   - Pastikan ponsel & komputer terhubung ke jaringan yang sama")
    print("   - Catat alamat IP ponsel (biasanya terlihat di aplikasi)")
    
    print("\n2. Uji Koneksi:")
    response = input("Uji koneksi ke kamera Android sekarang? (y/n): ")
    
    if response.lower() in ['y', 'yes']:
        test_android_camera_connection()
    
    print("\n3. Integrasi dengan VTuber Tracker:")
    ip_ponsel = input("Masukkan IP ponsel untuk integrasi (kosongkan jika tidak): ").strip()
    
    if ip_ponsel:
        integrate_with_vtuber_tracker(ip_ponsel)
    
    print("\nTips Tambahan:")
    print("- Pastikan jaringan stabil untuk kualitas streaming terbaik")
    print("- Gunakan mode Landscape di IP Webcam untuk orientasi yang benar") 
    print("- Atur kualitas video di IP Webcam (resolusi & bitrate) sesuai kebutuhan")
    print("- Jika mengalami latensi tinggi, kurangi resolusi atau bitrate")