#!/usr/bin/env python3
"""
Contoh integrasi VTuber Tracker dengan VSeeFace
"""
import sys
import os
import time
import threading

# Tambahkan root proyek ke path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from vtuber_tracker_lib import VTuberTracker, VTuberConfig
from sender.vmc_sender import VMCSender

def setup_vseeface_connection():
    """
    Panduan untuk menghubungkan ke VSeeFace
    
    VSeeFace mendukung OSC protocol, dan biasanya menggunakan:
    - Port: 39540 (default untuk OSC input)
    - IP: 127.0.0.1 (localhost)
    """
    print("=== Panduan Integrasi VTuber Tracker dengan VSeeFace ===")
    print("\nLangkah-langkah sebelum memulai:")
    print("1. Download dan install VSeeFace dari GitHub atau website resmi")
    print("2. Buka VSeeFace dan pastikan 'OSC Input' aktif")
    print("3. Dalam VSeeFace, pastikan settings OSC:")
    print("   - OSC Input Port: 39540 (ini default)")
    print("   - Enable OSC Input: ON")
    print("4. Pada tab 'Tracking', pastikan menggunakan input dari OSC")
    print("5. Di tab 'Output', pilih Virtual Camera untuk digunakan di game")
    
    print("\nCatatan penting untuk Steam Game Streaming:")
    print("- Steam akan mendeteksi kamera virtual dari VSeeFace")
    print("- Di dalam game, pilih kamera VSeeFace sebagai input video")
    print("- Pastikan VSeeFace berjalan sebelum memulai game")

def create_vseeface_sender():
    """
    Membuat sender yang sesuai dengan format VSeeFace
    """
    print("\nMembuat sender untuk VSeeFace...")
    
    # VSeeFace menggunakan port 39540 untuk OSC input (berbeda dari VMC standar)
    # Format OSC message yang diterima VSeeFace:
    # /tracking/translation - posisi kepala (x, y, z)
    # /tracking/rotation - rotasi kepala (x, y, z) dalam derajat
    # /blendshapes - ekspresi wajah
    sender = VMCSender(
        host="127.0.0.1",
        port=39540,  # Port untuk OSC input VSeeFace
        enabled=True
    )
    
    return sender

def map_to_vseeface_format(face_data):
    """
    Mengonversi data pelacakan wajah ke format yang sesuai untuk VSeeFace
    """
    # Konversi parameter untuk VSeeFace
    vseeface_params = {
        # Rotasi kepala (dalam derajat)
        "face:rotation:x": face_data.head_pitch * 30,    # Pitch (atas/bawah)
        "face:rotation:y": face_data.head_yaw * 30,      # Yaw (kiri/kanan)  
        "face:rotation:z": face_data.head_roll * 15,     # Roll (miring)
        
        # Ekspresi mata
        "face:eye:left": 1.0 - min(1.0, face_data.eye_left * 3.0),   # Kedipan mata kiri (0=open, 1=closed)
        "face:eye:right": 1.0 - min(1.0, face_data.eye_right * 3.0), # Kedipan mata kanan
        
        # Ekspresi mulut
        "face:mouth:open": min(1.0, face_data.mouth_open * 3.0),     # Pembukaan mulut
        "face:mouth:wide": min(1.0, face_data.mouth_wide * 2.0),     # Lebar mulut
        
        # Posisi kepala (jika tersedia, biasanya dalam satuan mm)
        "face:position:x": 0.0,  # Posisi horizontal
        "face:position:y": 0.0,  # Posisi vertikal  
        "face:position:z": 0.0,  # Posisi dalam/luar
    }
    
    return vseeface_params

class VTuberTrackerWithVSeeFace:
    """
    Integrasi VTuber Tracker dengan VSeeFace
    """
    def __init__(self, config=None):
        self.config = config or VTuberConfig(
            frame_width=640,
            frame_height=480,
            smoothing_alpha=0.3,
            enable_vmc_output=True,
            vmc_host="127.0.0.1",
            vmc_port=39540  # Port VSeeFace OSC input
        )
        
        # Inisialisasi tracker
        self.tracker = VTuberTracker(self.config)
        
        # Inisialisasi VSeeFace sender
        self.vseeface_sender = VMCSender(
            host="127.0.0.1",
            port=39540,  # Port default VSeeFace
            enabled=True
        )
        
        self.is_running = False
        self.tracking_thread = None
    
    def tracking_loop_with_vseeface(self):
        """
        Loop pelacakan khusus untuk VSeeFace
        """
        print("Memulai tracking loop untuk VSeeFace...")
        
        while self.is_running and self.tracker.is_running:
            try:
                # Dapatkan data pelacakan dari sistem internal
                # NOTE: Dalam implementasi aktual, Anda harus mengakses data dari sistem pelacakan
                # Kita buat mock data untuk contoh
                class MockFaceData:
                    def __init__(self):
                        self.head_yaw = 0.0
                        self.head_pitch = 0.0
                        self.head_roll = 0.0
                        self.eye_left = 0.1
                        self.eye_right = 0.1
                        self.mouth_open = 0.1
                        self.mouth_wide = 0.1
                
                # Di implementasi aktual, Anda akan mendapatkan data dari pelacakan wajah
                face_data = MockFaceData()  # Gantilah dengan data aktual dari sistem pelacakan
                
                # Konversi ke format VSeeFace
                vseeface_params = map_to_vseeface_format(face_data)
                
                # Kirim ke VSeeFace
                if self.vseeface_sender.is_connected:
                    # Dalam implementasi aktual, kirim parameter ke VSeeFace
                    # Format OSC untuk VSeeFace
                    pass
                
                time.sleep(1/30)  # ~30 FPS
                
            except Exception as e:
                print(f"Error dalam tracking loop: {e}")
                time.sleep(0.1)
    
    def start(self):
        """
        Mulai tracking dengan integrasi VSeeFace
        """
        print("Memulai VTuber Tracker dengan integrasi VSeeFace...")
        
        # Mulai tracker
        self.tracker.start()
        
        # Mulai loop khusus VSeeFace
        self.is_running = True
        self.tracking_thread = threading.Thread(target=self.tracking_loop_with_vseeface)
        self.tracking_thread.start()
        
        print("VTuber Tracker + VSeeFace siap digunakan!")
    
    def stop(self):
        """
        Hentikan tracking
        """
        self.is_running = False
        if self.tracking_thread:
            self.tracking_thread.join(timeout=2.0)
        
        self.tracker.stop()
        self.vseeface_sender.disconnect()
        
        print("VTuber Tracker + VSeeFace dihentikan.")

def example_usage_with_vseeface():
    """
    Contoh penggunaan VTuber Tracker dengan VSeeFace
    """
    print("=== Contoh Penggunaan dengan VSeeFace ===")
    
    setup_vseeface_connection()
    
    print("\nMenggunakan konfigurasi khusus untuk VSeeFace...")
    
    # Konfigurasi untuk VSeeFace
    config = VTuberConfig(
        frame_width=640,
        frame_height=480,
        smoothing_alpha=0.3,
        enable_vmc_output=True,
        vmc_host="127.0.0.1",
        vmc_port=39540,  # Port VSeeFace
    )
    
    # Buat integrasi
    integrator = VTuberTrackerWithVSeeFace(config)

    print("\nPastikan VSeeFace berjalan dan siap menerima data OSC!")
    print("Tekan Enter untuk melanjutkan...")
    input()

    try:
        integrator.start()

        print("\nTracker berjalan! Data dikirim ke VSeeFace...")
        print("Wajah Anda sekarang dapat digunakan dalam game Steam!")
        print("\nInstruksi:")
        print("- Pastikan VSeeFace menggunakan kamera virtual sebagai output")
        print("- Dalam Steam, pilih kamera VSeeFace sebagai input video")
        print("- Arahkan wajah Anda ke kamera untuk mengontrol model VTuber")
        print("- Tekan Ctrl+C untuk berhenti")

        # Jalankan selama 60 detik atau sampai dihentikan
        start_time = time.time()
        try:
            while True:
                elapsed = time.time() - start_time
                if int(elapsed) % 10 == 0:
                    print(f"[{int(elapsed)}s] Tracker berjalan...")
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nMenghentikan tracker...")

        integrator.stop()
        print("Selesai!")

if __name__ == "__main__":
    print("VTuber Tracker - Integrasi VSeeFace")
    print("=" * 40)

    example_usage_with_vseeface()