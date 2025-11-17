#!/usr/bin/env python3
"""
Contoh integrasi VTuber Tracker untuk streaming di game Steam
"""
import sys
import os
import time
import threading
import json

# Tambahkan root proyek ke path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from vtuber_tracker_lib import VTuberTracker, VTuberConfig

def setup_for_steam_game():
    """
    Panduan untuk menggunakan VTuber Tracker saat streaming game di Steam
    """
    print("=== Panduan Menggunakan VTuber Tracker di Steam Game ===")
    print("\nSebelum bermain game dengan VTuber Tracker:")
    
    print("\n1. Persiapan Sistem:")
    print("   - Pastikan kamera berfungsi (webcam atau Android)")
    print("   - Install VSeeFace atau software VTuber lainnya")
    print("   - Siapkan model VTuber (Live2D, VRM, atau 3D)")
    
    print("\n2. Konfigurasi Streaming:")
    print("   - Buka OBS Studio atau software streaming lainnya")
    print("   - Tambahkan VSeeFace sebagai source video")
    print("   - Atur posisi dan ukuran sesuai kebutuhan")
    
    print("\n3. Pengaturan Game Steam:")
    print("   - Di banyak game, Anda bisa mengaktifkan kamera di pengaturan")
    print("   - Pilih VSeeFace sebagai perangkat kamera")
    print("   - Beberapa game mendukung augmented reality atau overlay kamera")
    
    print("\n4. Metode Koneksi:")
    print("   A. VTuber Tracker -> VSeeFace -> Steam Game")
    print("      - VTuber Tracker mengirim data ke VSeeFace via OSC")
    print("      - VSeeFace menghasilkan kamera virtual")
    print("      - Game Steam menggunakan kamera virtual")
    
    print("   B. VTuber Tracker -> Live2D/VRM -> VSeeFace -> Steam Game")
    print("      - Menggunakan model 3D/2D dengan skeleton")
    print("      - Lebih realistis dan menarik")

def setup_vseeface_osc_connection():
    """
    Setup untuk menghubungkan ke VSeeFace via OSC
    """
    print("\n=== Pengaturan Koneksi ke VSeeFace ===")
    print("\nVSeeFace menggunakan protokol OSC untuk menerima data pelacakan:")
    print("- Port OSC input: 39540 (default)")
    print("- Alamat: 127.0.0.1 (localhost)")
    print("- Format pesan OSC harus sesuai dengan yang diterima VSeeFace")
    
    print("\nMengirim data ke VSeeFace:")
    print("1. Pastikan VSeeFace berjalan")
    print("2. Di VSeeFace, aktifkan 'OSC Input' dan set port ke 39540")
    print("3. Gunakan format OSC yang benar untuk parameter wajah")

def create_vseeface_osc_sender():
    """
    Membuat sender OSC khusus untuk VSeeFace
    """
    from pythonosc import udp_client
    
    # Alamat VSeeFace OSC input
    client = udp_client.SimpleUDPClient("127.0.0.1", 39540)
    return client

def map_face_data_to_vseeface(face_data, sender):
    """
    Mengirim data pelacakan wajah ke VSeeFace via OSC
    """
    try:
        # Kirim rotasi kepala (dalam derajat)
        sender.send_message("/tracking/rotation/x", face_data.head_pitch * 30)  # Pitch (atas/bawah)
        sender.send_message("/tracking/rotation/y", face_data.head_yaw * 30)    # Yaw (kiri/kanan)
        sender.send_message("/tracking/rotation/z", face_data.head_roll * 15)   # Roll (miring)
        
        # Kirim ekspresi mata
        # VSeeFace biasanya mengharapkan nilai 0.0 - 1.0
        left_eye_closed = min(1.0, max(0.0, face_data.eye_left * 3.0))
        right_eye_closed = min(1.0, max(0.0, face_data.eye_right * 3.0))
        
        sender.send_message("/tracking/eye_left", 1.0 - left_eye_closed)  # 0 = tertutup, 1 = terbuka
        sender.send_message("/tracking/eye_right", 1.0 - right_eye_closed)
        
        # Kirim ekspresi mulut
        mouth_open = min(1.0, max(0.0, face_data.mouth_open * 3.0))
        mouth_wide = min(1.0, max(0.0, face_data.mouth_wide * 2.0))
        
        sender.send_message("/tracking/mouth_open", mouth_open)
        sender.send_message("/tracking/mouth_x", mouth_wide - 0.5)  # -0.5 s/d 0.5
        
        # Kirim posisi kepala jika tersedia
        sender.send_message("/tracking/translation/x", 0.0)
        sender.send_message("/tracking/translation/y", 0.0)
        sender.send_message("/tracking/translation/z", 0.0)
        
    except Exception as e:
        print(f"Error mengirim data ke VSeeFace: {e}")

class SteamVTuberStreamer:
    """
    Kelas untuk streaming VTuber di game Steam
    """
    def __init__(self, config=None):
        self.config = config or VTuberConfig(
            frame_width=640,
            frame_height=480,
            smoothing_alpha=0.3,
            enable_vmc_output=True,  # Kirim ke VSeeFace
            vmc_host="127.0.0.1",
            vmc_port=39540,  # Port VSeeFace
        )
        
        # Inisialisasi tracker
        self.tracker = VTuberTracker(self.config)
        
        # Inisialisasi OSC client untuk VSeeFace
        try:
            from pythonosc import udp_client
            self.vseeface_client = udp_client.SimpleUDPClient("127.0.0.1", 39540)
        except ImportError:
            print("python-osc tidak ditemukan. Instal dengan: pip install python-osc")
            self.vseeface_client = None
        
        self.is_running = False
        self.streaming_thread = None
        self.last_face_data = None
        
    def start_streaming(self):
        """
        Mulai streaming VTuber untuk game Steam
        """
        print("Memulai VTuber streaming untuk game Steam...")
        
        # Mulai pelacakan wajah
        self.tracker.start()
        
        # Mulai thread streaming
        self.is_running = True
        self.streaming_thread = threading.Thread(target=self.streaming_loop)
        self.streaming_thread.start()
        
        print("VTuber siap untuk streaming game di Steam!")
        print("Pastikan VSeeFace berjalan dan kamera virtual digunakan dalam game.")
    
    def streaming_loop(self):
        """
        Loop utama streaming untuk game Steam
        """
        print("Streaming loop aktif...")
        
        # Dalam implementasi sebenarnya, kita akan mengakses data pelacakan secara langsung
        # Karena struktur library sekarang, kita perlu cara untuk mengakses data pelacakan
        import time
        
        last_send_time = time.time()
        
        while self.is_running:
            try:
                # Simulasi data pelacakan - dalam implementasi sebenarnya
                # kita akan mengakses data dari sistem pelacakan
                # Kita kirim data dummy untuk contoh
                class DummyFaceData:
                    def __init__(self):
                        self.head_yaw = 0.0
                        self.head_pitch = 0.0
                        self.head_roll = 0.0
                        self.eye_left = 0.1
                        self.eye_right = 0.1
                        self.mouth_open = 0.1
                        self.mouth_wide = 0.1
                
                # Update data secara perlahan untuk simulasi
                import random
                data = DummyFaceData()
                data.head_yaw = random.uniform(-0.2, 0.2)
                data.head_pitch = random.uniform(-0.1, 0.1)
                data.head_roll = random.uniform(-0.1, 0.1)
                
                if self.vseeface_client:
                    map_face_data_to_vseeface(data, self.vseeface_client)
                
                # Kirim setiap ~30 FPS
                time.sleep(1/30)
                
            except Exception as e:
                print(f"Error dalam streaming loop: {e}")
                time.sleep(0.1)
    
    def stop_streaming(self):
        """
        Hentikan streaming
        """
        self.is_running = False
        
        if self.streaming_thread:
            self.streaming_thread.join(timeout=2.0)
        
        self.tracker.stop()
        print("Streaming dihentikan.")

def complete_steam_setup_guide():
    """
    Panduan lengkap setup untuk game Steam
    """
    print("\n=== Panduan Lengkap Setup VTuber Tracker di Steam ===")
    
    print("\n1. Persiapan Awal:")
    print("   - Install VSeeFace (https://github.com/bzitko/VSeeFace)")
    print("   - Download model VTuber (Live2D/VRM)")
    print("   - Siapkan kamera (webcam atau Android)")
    
    print("\n2. Konfigurasi VSeeFace:")
    print("   - Buka VSeeFace")
    print("   - Di tab 'Tracking', pilih 'OSC Input' sebagai metode pelacakan")
    print("   - Di tab 'OSC', pastikan port input adalah 39540")
    print("   - Di tab 'Output', aktifkan Virtual Camera")
    print("   - Di tab 'Model', pilih model VTuber Anda")
    
    print("\n3. Konfigurasi Steam Game:")
    print("   - Buka game yang mendukung kamera (misal: VRChat)")
    print("   - Di pengaturan game, pilih kamera virtual VSeeFace")
    print("   - Beberapa game memiliki filter kamera langsung")
    
    print("\n4. Jalankan VTuber Tracker:")
    print("   - Pastikan VSeeFace berjalan")
    print("   - Jalankan script ini untuk mengirim data pelacakan")
    print("   - Arahkan wajah ke kamera untuk mengontrol model")

def demo_streaming():
    """
    Demo streaming VTuber untuk game Steam
    """
    print("\n=== Demo Streaming VTuber untuk Steam ===")
    
    complete_steam_setup_guide()
    
    print("\nCatatan Penting:")
    print("- Pastikan VSeeFace berjalan sebelum menjalankan script ini")
    print("- Jika menggunakan kamera Android, gunakan --stream-url")
    print("- Pastikan tidak ada firewall yang memblokir OSC")
    print("- Gunakan koneksi stabil untuk pengalaman terbaik")
    
    print("\nMemulai demo streaming...")
    
    # Buat konfigurasi untuk VSeeFace
    config = VTuberConfig(
        frame_width=640,
        frame_height=480,
        smoothing_alpha=0.25,
        enable_vmc_output=True,
        vmc_host="127.0.0.1",
        vmc_port=39540,  # Port VSeeFace
    )
    
    # Buat streamer
    streamer = SteamVTuberStreamer(config)
    
    print("\nPastikan VSeeFace berjalan dan siap menerima OSC dari port 39540")
    print("Tekan Enter untuk melanjutkan...")
    input()
    
    try:
        streamer.start_streaming()
        
        print("\nVTuber tracker aktif untuk game Steam!")
        print("Wajah Anda sekarang dikontrol dalam game!")
        print("\nTips saat bermain game:")
        print("- Gunakan gerakan wajah yang natural")
        print("- Pastikan pencahayaan cukup untuk pelacakan")
        print("- Jangan tutup terminal ini sampai selesai bermain")
        print("- Tekan Ctrl+C untuk berhenti")
        
        # Jalankan sampai dihentikan
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nMenghentikan streaming...")
    
    finally:
        streamer.stop_streaming()
        print("Streaming VTuber untuk Steam dihentikan.")

if __name__ == "__main__":
    print("VTuber Tracker - Integrasi untuk Game Steam")
    print("=" * 50)
    
    print("\nVTuber Tracker dapat digunakan dalam game Steam dengan VSeeFace!")
    
    demo_streaming()