# VTuber Tracker - One-Command Setup & Run Guide

## ✅ Sudah Diuji: Bisa Berjalan hanya dengan `python main.py`

Proyek ini telah dioptimalkan sehingga bisa berjalan hanya dengan satu perintah:

```bash
python main.py
```

## 🚀 Cara Penggunaan Super-Simple:

### **1. Clone Repository:**
```bash
git clone https://github.com/Yoriyoi-drop/vtuber-tracker.git
cd vtuber-tracker
```

### **2. Install Dependencies:**
```bash
pip install opencv-python mediapipe pyqt5 python-osc websocket-client requests numpy pyfakewebcam
```

### **3. Jalankan Aplikasi:**
```bash
python main.py                    # GUI mode (default)
python main.py --mode cli         # CLI mode
python main.py --help             # Tampilkan semua opsi
```

## 🎯 Fitur Utama:
- **Pelacakan wajah real-time** dengan MediaPipe
- **Output ke VSeeFace/VMC** untuk digunakan di semua software VTuber
- **Kalibrasi posisi netral** untuk wajah
- **Kontrol sensitivitas lanjutan** untuk semua parameter wajah
- **Mode presisi tinggi** untuk gerakan halus
- **Pengaturan deadzone** untuk mengurangi noise
- **Virtual camera output** untuk digunakan di game/streaming
- **Kamera Android support** melalui IP Webcam
- **GUI intuitif** untuk kontrol langsung
- **CLI mode** untuk penggunaan headless

## 📋 Mode Penggunaan:
- **GUI**: `python main.py` - Mode grafis dengan kontrol lengkap
- **CLI**: `python main.py --mode cli` - Mode command-line untuk headless
- **Kamera Spesifik**: `python main.py --camera 1` - Gunakan kamera indeks 1
- **Android Camera**: `python main.py --stream-url http://192.168.1.100:8080/video`

## ✅ Platform yang Didukung:
- **Windows 10/11**
- **macOS** (Intel & Apple Silicon)
- **Linux** (Ubuntu, Debian, Fedora, Arch, dll.)

## 🎮 Kompatibel Dengan:
- **VSeeFace** - Virtual Motion Capture
- **VTube Studio** - WebSocket integration
- **Live2D Cubism** - Model 2D
- **VRM Models** - Model 3D dari VRoid Studio
- **Semua platform streaming** - Twitch, YouTube, Zoom, Discord, VRChat, dll.

## 📦 Struktur Proyek:
```
vtuber-tracker/
├── main.py                 ← [FILE UTAMA] - JALANKAN INI SAJA
├── run_app.py              - Backend runner (dipanggil oleh main.py)
├── vtuber_tracker_lib.py   - Core library
├── config/                 - File konfigurasi
├── tracker/                - Modul pelacakan
├── sender/                 - Modul output
├── gui/                    - Modul GUI
├── examples/               - Contoh penggunaan
└── README.md               - Dokumentasi
```

## 🔧 File Konfigurasi:
- Secara default menggunakan `config/config.json`
- Dapat dioverride dengan argumen command-line
- Parameter sensitivitas, deadzone, dan presisi dapat diatur melalui GUI

## 🌐 Output Protocols:
- **VMC (Virtual Motion Capture)** - Kompatibel dengan VSeeFace, VTube Studio
- **OSC Protocol** - Untuk aplikasi kustom
- **Virtual Camera** - Output ke kamera virtual untuk semua aplikasi

## 💡 Tips Penggunaan:
1. **Untuk pemula**: Jalankan `python main.py` saja, gunakan GUI untuk kalibrasi
2. **Untuk streaming headless**: Gunakan `python main.py --mode cli` 
3. **Untuk kamera Android**: Install IP Webcam di ponsel, lalu gunakan `--stream-url`
4. **Untuk kamera spesifik**: Gunakan `--camera [indeks]` jika punya lebih dari satu kamera

---

**SELAMAT! Anda sekarang memiliki VTuber Tracker yang siap pakai hanya dengan satu perintah: `python main.py`** 🚀