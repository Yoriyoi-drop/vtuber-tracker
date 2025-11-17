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

## Kontribusi
Proyek ini terbuka untuk kontribusi. Silakan lihat [CONTRIBUTING.md](CONTRIBUTING.md) untuk panduan berkontribusi.

## Lisensi
Proyek ini dilisensikan di bawah [MIT License](LICENSE).