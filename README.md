# VTuber Tracker - Library Python untuk Pelacakan Wajah

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

Library Python yang menyediakan fungsi pelacakan wajah untuk aplikasi VTuber. Dapat digunakan untuk streaming jangka panjang dengan output ke perangkat lunak seperti VSeeFace, OBS, Zoom, dll.

## Instalasi
- **[Klik di sini untuk panduan instalasi dalam bahasa Indonesia](CARA_INSTALL.md)** - Panduan lengkap instalasi untuk Windows, macOS, dan Linux dengan langkah-langkah untuk pemula

## Fitur Utama
- **Pelacakan Wajah Real-Time** - Menggunakan MediaPipe untuk deteksi landmark wajah
- **Kalibrasi Posisi Netral** - Fungsi untuk menetapkan posisi wajah netral
- **Kontrol Sensitivitas Lanjutan** - Pengaturan per parameter wajah (yaw, pitch, roll, mata, mulut)
- **Mode Presisi Tinggi** - Penguatan sinyal untuk gerakan halus
- **Pengaturan Deadzone** - Ambang batas minimum untuk mengurangi noise
- **Output VMC (Virtual Motion Capture)** - Kompatibel dengan VSeeFace dan perangkat lunak lain
- **Virtual Camera Output** - Output ke kamera virtual untuk digunakan di aplikasi lain
- **Smoothing Gerakan** - Peredaman untuk mengurangi抖动 pada gerakan

## Instalasi

### Prasyarat
- Python 3.8 atau lebih baru
- Sistem operasi: Windows, macOS, atau Linux

### Instalasi Dependensi
```bash
pip install opencv-python mediapipe pyqt5 python-osc websocket-client requests numpy pyfakewebcam
```

### Instalasi Library
```bash
# Clone repository
git clone https://github.com/Yoriyoi-drop/vtuber-tracker.git
cd vtuber-tracker

# Install dalam mode pengembangan
pip install -e .
```

## Menggunakan Kamera Android

VTuber Tracker mendukung penggunaan kamera dari ponsel Android melalui IP Webcam:

### 1. Pengaturan Kamera Android
1. Install aplikasi IP Webcam di ponsel Android (misalnya "IP Webcam" dari Pavel Khlebovich)
2. Pastikan ponsel dan komputer terhubung ke jaringan Wi-Fi yang sama
3. Buka aplikasi IP Webcam dan tekan "Start Server"
4. Catat alamat IP dan port yang ditampilkan (misalnya `192.168.1.100:8080`)

### 2. Menggunakan dengan Aplikasi
```bash
# Jalankan dengan URL stream kamera Android
python run_app.py --stream-url http://192.168.1.100:8080/video
```

### 3. Menggunakan dengan Library
```python
from vtuber_tracker_lib import VTuberTracker, VTuberConfig

config = VTuberConfig(
    stream_url="http://192.168.1.100:8080/video",  # URL dari IP Webcam
    frame_width=640,
    frame_height=480,
    enable_vmc_output=True
)

tracker = VTuberTracker(config)
tracker.start()
```

Lihat [examples/android_camera_integration.py](examples/android_camera_integration.py) untuk contoh implementasi lengkap.

## Cara Penggunaan Dasar

### 1. Penggunaan Sederhana
```python
from vtuber_tracker_lib import VTuberTracker, VTuberConfig

# Buat konfigurasi
config = VTuberConfig()

# Buat tracker
tracker = VTuberTracker(config)

# Mulai pelacakan
tracker.start()

# Berhenti pelacakan setelah selesai
tracker.stop()
```

### 2. Penggunaan dengan Konfigurasi Khusus
```python
from vtuber_tracker_lib import VTuberTracker, VTuberConfig

# Buat konfigurasi khusus
config = VTuberConfig(
    camera_index=0,
    frame_width=640,
    frame_height=480,
    smoothing_alpha=0.2,
    enable_virtual_camera=True,
    enable_vmc_output=True,
    vmc_host="127.0.0.1",
    vmc_port=39539
)

# Buat dan jalankan tracker
tracker = VTuberTracker(config)
tracker.start()

# Lakukan kalibrasi jika diperlukan
tracker.start_calibration()

# Aktifkan mode presisi
tracker.enable_precision_mode(enabled=True, multiplier=1.5)

# Cek status kalibrasi
if tracker.is_calibrated():
    print("Kalibrasi selesai")

# Berhenti setelah selesai
import time
time.sleep(60)  # Jalankan selama 1 menit
tracker.stop()
```

### 3. Integrasi dengan Aplikasi Lain
```python
from vtuber_tracker_lib import VTuberTracker, VTuberConfig

class MyApp:
    def __init__(self):
        config = VTuberConfig(
            enable_virtual_camera=False,  # Jika hanya ingin output ke VMC
            enable_vmc_output=True
        )
        self.tracker = VTuberTracker(config)

    def start_streaming(self):
        self.tracker.start()

    def stop_streaming(self):
        self.tracker.stop()
```

## Penggunaan untuk Streaming Jangka Panjang
- Library dirancang untuk penggunaan jangka panjang (>10 jam)
- Mode CLI lebih ringan daripada GUI
- Sistem manajemen memori yang efisien
- Penanganan kesalahan yang robust

## Konfigurasi Lanjutan
Semua pengaturan dapat dikonfigurasi melalui objek `VTuberConfig`:
- `camera_index` - Indeks kamera (0, 1, 2, dst)
- `frame_width`, `frame_height` - Resolusi kamera
- `smoothing_alpha` - Parameter smoothing (0.0-1.0, nilai rendah = lebih smooth)
- `enable_smoothing` - Aktifkan/nonaktifkan smoothing
- `enable_virtual_camera` - Aktifkan output ke kamera virtual
- `virtual_camera_width`, `virtual_camera_height` - Resolusi kamera virtual
- `virtual_camera_fps` - Frame rate kamera virtual
- `vmc_host`, `vmc_port` - Alamat dan port untuk output VMC
- `enable_vmc_output` - Aktifkan output ke perangkat lunak VMC

## Integrasi dengan Platform Streaming

VTuber Tracker kompatibel dengan semua platform streaming utama:

### 1. VSeeFace (Core Engine)
- Kirim parameter pelacakan wajah melalui protokol OSC
- Port default: 39539 (VMC protocol)
- Support untuk Live2D dan VRM model
- Output sebagai kamera virtual untuk platform lain
- Lihat [examples/vseeface_integration.py](examples/vseeface_integration.py)

### 2. Game Streaming
- **VRChat**: Menggunakan kamera virtual VSeeFace
- **Steam Games**: Dengan VSeeFace sebagai input kamera
- Lihat [examples/steam_game_integration.py](examples/steam_game_integration.py)

### 3. Live Streaming
- **Twitch**: Melalui OBS Studio dengan VSeeFace sebagai sumber
- **YouTube Live**: Melalui OBS Studio atau langsung
- **Facebook Live**: Melalui OBS Studio
- Menggunakan VSeeFace sebagai sumber kamera virtual

### 4. Video Conference
- **Zoom**: Pilih VSeeFace sebagai kamera video
- **Discord**: Pilih VSeeFace sebagai input video
- **Microsoft Teams, Google Meet**: Kompatibel melalui kamera virtual

### 6. Lainnya
- **Recording**: Dapat digunakan untuk merekam VTuber
- **Broadcasting**: Mendukung berbagai protokol streaming
- Lihat [examples/all_platforms_support.py](examples/all_platforms_support.py) untuk panduan lengkap

### 7. Live2D Cubism
- Kirim parameter pelacakan wajah melalui OSC ke Live2D Cubism
- Format parameter: `angle_x`, `angle_y`, `angle_z`, `eye_l_open`, `mouth_open`, dll
- Cocok untuk model yang dioptimalkan untuk animasi real-time

### 8. VRM (3D Model)
- Gunakan model VRM dalam aplikasi seperti VRoid Studio
- Parameter pelacakan dikirim ke aplikasi 3D (seperti VTube Studio)
- Mendukung blendshape untuk ekspresi wajah

### 9. Spine 2D Skeletal Animation
- Gunakan skeleton 2D dengan Spine
- Parameter mengontrol bone dalam struktur 2D
- Efisien untuk animasi 2D berkualitas tinggi

### 10. Format OSC untuk Software VTuber
VTuber Tracker menghasilkan parameter pelacakan wajah yang dapat dikirim melalui protokol OSC ke berbagai software:

Untuk VMC Protocol (VSeeFace, VTube Studio, etc):
```
/VMC/Ext/Root/Rot   -> Rotasi kepala (quaternion)
/VMC/Ext/Blend/Val  -> Ekspresi wajah (blink, mouth, dll)
```

Lihat [examples/3d_model_integration.py](examples/3d_model_integration.py) untuk contoh konversi parameter.

## Mendukung Hybrid Python-C++

Proyek ini sekarang mendukung integrasi antara Python dan C++ untuk performa maksimum:

### 1. Struktur Hybrid
- **Python Layer**: Antarmuka tingkat tinggi dan mudah digunakan
- **C++ Core**: Performa tinggi untuk pelacakan wajah dan pemrosesan real-time
- **Bridge**: Komunikasi antara Python dan C++ menggunakan pybind11

### 2. Manfaat Pendekatan Hybrid
- **Kecepatan**: Pemrosesan intensif di C++ untuk latensi rendah
- **Fleksibilitas**: Kemudahan pengembangan di Python
- **Efisiensi**: Penggunaan resource yang optimal
- **Portabilitas**: Dapat dijalankan di semua platform

### 3. Library yang Digunakan

#### Python Libraries (10):
1. OpenCV-Python - Computer vision dan image processing
2. MediaPipe - Framework pelacakan landmark wajah dan pose tubuh
3. NumPy - Operasi matematika dan array multidimensional
4. SciPy - Scientific computation dan algoritma numerik
5. PyQt5/6 - GUI framework untuk aplikasi desktop
6. python-osc - Komunikasi OSC untuk VMC (Virtual Motion Capture)
7. PyFakeWebcam - Virtual camera output untuk sistem
8. SoundDevice - Manipulasi audio (jika diperlukan untuk audio sync)
9. Requests - HTTP library untuk REST API integrasi
10. Numba - Acceleration untuk komputasi numerik

#### C++ Libraries (10):
1. OpenCV C++ - Computer vision library dengan performa tinggi
2. MediaPipe C++ - Native MediaPipe untuk performa maksimum
3. Eigen3 - Linear algebra library untuk transformasi 3D
4. Boost - Koleksi library C++ standar tambahan
5. OpenSceneGraph - Rendering 3D untuk model VTuber
6. PCL (Point Cloud Library) - 3D point cloud processing
7. FFmpeg - Video/audio encoding/decoding dan streaming
8. WebSocket++ - Komunikasi real-time untuk networking
9. GLM - OpenGL Mathematics untuk grafik 3D
10. TinyXML2 - Parsing XML untuk konfigurasi dan metadata

### 4. Penggunaan Hybrid
```python
from python_cpp_bridge import CppFaceTrackerBridge

# Create hybrid tracker
bridge = CppFaceTrackerBridge()

# Process with C++ acceleration
tracking_data = bridge.process_frame(landmarks)

# Use Python for high-level orchestration
# while C++ handles intensive computations
```

Lihat [cpp/](cpp/) untuk implementasi C++ dan [python_cpp_bridge.py](python_cpp_bridge.py) untuk contoh bridge.

## Troubleshooting
- Jika kamera tidak ditemukan, pastikan tidak digunakan aplikasi lain
- Tambahkan user ke grup video di Linux: `sudo usermod -a -G video $USER`
- Pastikan semua dependensi terinstal dengan benar
- Cek perangkat kamera dengan: `ls /dev/video*` (Linux) atau device manager (Windows)

## Deteksi dan Troubleshooting Kamera
Library ini menyertakan utilitas untuk membantu mendeteksi dan menguji kamera:

### 1. Deteksi Kamera Tersedia
```bash
python camera_util.py detect
```
Fungsi ini akan mendeteksi semua kamera yang tersedia dan menampilkan informasi tentangnya.

### 2. Test Kamera Spesifik
```bash
python camera_util.py test 0 10  # Test kamera indeks 0 selama 10 detik
```
Fungsi ini akan menampilkan feed kamera secara real-time untuk pengujian.

### 3. Rekomendasi Kamera Otomatis
Library secara otomatis akan mendeteksi kamera yang tersedia dan menggunakan kamera pertama yang ditemukan jika kamera konfigurasi tidak tersedia.

## Integrasi dengan OBS Studio
Library juga mendukung penggunaan OBS Virtual Camera sebagai sumber input. Ini memungkinkan workflow streaming yang lebih kompleks dengan efek tambahan di OBS.

### Setup OBS Virtual Camera:
1. Di OBS: `Tools` > `Virtual Camera` > `Start Virtual Camera`
2. Kamera OBS sekarang bisa digunakan sebagai input untuk library
3. Lihat `obs_integration.md` untuk panduan lengkap

## Fitur yang Dapat Dikembangkan
- Preset sistem kalibrasi
- AI-powered gesture recognition
- Multi-face tracking
- Cloud sync capabilities
- Plugin architecture

## Status Implementasi
- ✅ Virtual camera output
- ✅ CLI dan GUI mode
- ✅ Kalibrasi wajah
- ✅ Kontrol sensitivitas lanjutan
- ✅ Mode presisi tinggi
- ✅ Pengaturan deadzone
- ✅ Output VMC
- ✅ Streaming jangka panjang
- ✅ Android camera support
- ✅ 3D/2D model integration
- ✅ VSeeFace compatibility
- ✅ All streaming platforms support
- ✅ Hybrid Python-C++ implementation
- ✅ Complete documentation in Indonesian

## Versi dan Status Komplet
- **Versi**: 1.0.0 (Production Ready)
- **Kompletitas**: 95%
- **Status**: Stabil dan siap produksi
- Lihat [VERSION_INFO.md](VERSION_INFO.md) untuk detail evaluasi.

## Cara Penggunaan Cepat

### 1. Instalasi Cepat (Unix/Linux/macOS)
```bash
# Clone repository
git clone https://github.com/Yoriyoi-drop/vtuber-tracker.git
cd vtuber-tracker

# Jalankan script instalasi cepat
chmod +x startup.sh
./startup.sh
```

### 2. Instalasi Manual
```bash
# Clone repository
git clone https://github.com/Yoriyoi-drop/vtuber-tracker.git
cd vtuber-tracker

# Install dependencies
pip install opencv-python mediapipe pyqt5 python-osc websocket-client requests numpy pyfakewebcam

# Install dalam mode development
pip install -e .
```

### 3. Menjalankan Aplikasi
```bash
# Method 1: Menggunakan main.py (direkomendasikan)
python main.py                    # GUI mode dengan kamera default
python main.py --mode cli         # CLI mode
python main.py --mode gui         # GUI mode
python main.py --camera 1         # Gunakan kamera dengan indeks 1
python main.py --stream-url http://[ANDROID_IP]:8080/video  # Gunakan kamera Android
python main.py --help             # Tampilkan bantuan

# Method 2: Menggunakan run_app.py (lama)
python run_app.py                 # GUI mode dengan kamera default
python run_app.py --mode cli      # CLI mode
python run_app.py --stream-url http://[ANDROID_IP]:8080/video
```

`main.py` adalah file utama yang direkomendasikan untuk menjalankan aplikasi, karena:
- Menyediakan interface yang lebih user-friendly
- Melakukan pengecekan dependencies otomatis
- Memberikan informasi sistem dan instruksi yang jelas
- Menggabungkan semua fungsi dalam satu file mudah akses

### 4. Kompatibilitas Platform
- **Windows 10/11**: Dukungan penuh
- **macOS**: Dukungan penuh (Intel & Apple Silicon)
- **Linux**: Dukungan penuh (Ubuntu, Debian, Fedora, Arch, dll.)

## Kontribusi
Proyek ini terbuka untuk kontribusi. Silakan lihat [CONTRIBUTING.md](CONTRIBUTING.md) untuk panduan berkontribusi.

## Contoh Penggunaan
Lihat folder [examples/](examples/) untuk contoh-contoh penggunaan yang dapat membantu Anda memulai:

- [simple_example.py](examples/simple_example.py) - Contoh dasar penggunaan library
- [calibration_example.py](examples/calibration_example.py) - Demonstrasi proses kalibrasi dan penyesuaian sensitivitas
- [android_camera_example.py](examples/android_camera_example.py) - Panduan penggunaan kamera Android
- [android_camera_integration.py](examples/android_camera_integration.py) - Contoh integrasi kamera Android
- [3d_model_integration.py](examples/3d_model_integration.py) - Contoh integrasi dengan model 3/2D
- [vseeface_integration.py](examples/vseeface_integration.py) - Contoh integrasi dengan VSeeFace
- [steam_game_integration.py](examples/steam_game_integration.py) - Contoh penggunaan dalam game Steam
- [all_platforms_support.py](examples/all_platforms_support.py) - Panduan dukungan semua platform streaming
- [python_cpp_bridge.py](python_cpp_bridge.py) - Contoh integrasi hybrid Python-C++

## Arsitektur
Untuk dokumentasi arsitektur dan bagaimana sistem bekerja secara internal, lihat [ARCHITECTURE.md](ARCHITECTURE.md).

## Lisensi
Proyek ini dilisensikan di bawah [MIT License](LICENSE).