# Arsitektur VTuber Tracker

Dokumen ini menjelaskan struktur dan arsitektur proyek VTuber Tracker.

## Struktur Direktori

```
vtuber-tracker/
├── app.py                  # Aplikasi desktop utama dengan GUI
├── run_app.py             # Entry point utama aplikasi
├── vtuber_tracker_lib.py  # Library inti
├── config/                # File konfigurasi
├── tracker/               # Modul pelacakan wajah
│   ├── __init__.py
│   ├── camera.py          # Pengelolaan kamera
│   ├── face_tracking.py   # Modul pelacakan wajah dasar
│   ├── smoothing.py       # Smoothing gerakan
│   ├── calibration.py     # Modul kalibrasi
│   ├── landmarks_to_params.py  # Konversi landmark ke parameter
│   ├── precision_mode.py  # Mode presisi tinggi
│   └── virtual_camera.py  # Output kamera virtual
├── sender/                # Modul pengiriman data
│   ├── __init__.py
│   ├── vmc_sender.py      # Pengirim data VMC
│   └── vts_sender.py      # Pengirim data VTube Studio
├── gui/                   # Modul antarmuka pengguna
│   ├── __init__.py
│   └── main_gui.py        # GUI utama
├── examples/              # Contoh-contoh penggunaan
│   ├── simple_example.py
│   └── calibration_example.py
├── tests/                 # Test case
├── README.md
├── requirements.txt
├── setup.py
└── ...
```

## Komponen Utama

### 1. VTuberTracker (vtuber_tracker_lib.py)
Komponen utama yang menggabungkan semua sub-modul dan menyediakan API tingkat tinggi.

**Responsibilitas:**
- Mengelola semua komponen pelacakan
- Menyediakan metode untuk start/stop pelacakan
- Menyediakan API untuk kontrol kalibrasi dan mode presisi

### 2. FaceTracker (tracker/face_tracking.py)
Komponen yang menangani deteksi dan pelacakan landmark wajah menggunakan MediaPipe.

**Responsibilitas:**
- Mendeteksi landmark wajah dari frame kamera
- Menghitung parameter head pose (yaw, pitch, roll)
- Menghitung parameter ekspresi (mata, mulut)

### 3. CameraCapture (tracker/camera.py)
Komponen yang menangani akses kamera.

**Responsibilitas:**
- Mengakses perangkat kamera
- Mengambil frame dari kamera
- Menangani kesalahan akses kamera

### 4. DataSmoother (tracker/smoothing.py)
Komponen untuk smoothing data pelacakan.

**Responsibilitas:**
- Mengurangi jitter pada data pelacakan
- Menerapkan filter smoothing (saat ini exponential smoothing)

### 5. FaceCalibrator (tracker/calibration.py)
Komponen untuk kalibrasi posisi netral wajah.

**Responsibilitas:**
- Mengumpulkan sampel data untuk kalibrasi
- Menyimpan offset kalibrasi
- Menerapkan kalibrasi ke data pelacakan

### 6. LandmarksToParameters (tracker/landmarks_to_params.py)
Komponen untuk konversi landmark ke parameter kontrol.

**Responsibilitas:**
- Mengonversi landmark ke parameter wajah
- Menerapkan pengali sensitivitas
- Menerapkan deadzone

### 7. PrecisionMode (tracker/precision_mode.py)
Komponen untuk mode presisi tinggi.

**Responsibilitas:**
- Meningkatkan sensitivitas gerakan halus
- Mengurangi noise pada gerakan kecil

### 8. VMC Sender (sender/vmc_sender.py)
Komponen untuk output ke perangkat lunak VMC.

**Responsibilitas:**
- Mengirim data pelacakan via protokol OSC
- Berinteraksi dengan VSeeFace, VTube Studio, dll

### 9. Virtual Camera (tracker/virtual_camera.py)
Komponen untuk output ke kamera virtual.

**Responsibilitas:**
- Mengirim frame ke kamera virtual
- Berinteraksi dengan sistem operasi untuk kamera virtual

## Alur Data

1. **Akses Kamera** → `CameraCapture` mengambil frame dari perangkat kamera
2. **Pelacakan Wajah** → `FaceTracker` memproses frame untuk mendapatkan landmark
3. **Kalibrasi** → `FaceCalibrator` menerapkan offset kalibrasi ke data mentah
4. **Smoothing** → `DataSmoother` mengurangi noise pada data pelacakan
5. **Mode Presisi** → `PrecisionMode` mengoptimalkan data untuk gerakan halus
6. **Konversi Parameter** → `LandmarksToParameters` mengonversi ke parameter siap output
7. **Output** → Data dikirim ke `VMCSender` dan/atau `VirtualCamera`

## Konfigurasi

Konfigurasi aplikasi dikelola melalui kelas `VTuberConfig` yang menyediakan semua parameter yang dapat dikonfigurasi:

- Parameter kamera (indeks, resolusi)
- Parameter smoothing
- Parameter sensitivitas
- Pengaturan output (VMC, kamera virtual)
- Parameter kalibrasi
- Parameter mode presisi

## Pengembangan

### Tambah Fitur Baru
1. Tambahkan modul baru di folder terkait
2. Impor dan integrasikan ke `VTuberTracker`
3. Tambah opsi konfigurasi ke `VTuberConfig` jika diperlukan
4. Tambahkan test case di folder `tests/`
5. Perbarui dokumentasi

### Tambah Output Baru
1. Buat kelas baru di folder `sender/` mengikuti interface sender
2. Tambahkan konfigurasi ke `VTuberConfig`
3. Impor dan integrasikan ke `VTuberTracker`
4. Tambahkan test case

### Perbaikan Kinerja
- Optimasi pipeline pelacakan wajah
- Gunakan threading untuk komponen yang bisa diparalel
- Implementasi object pooling untuk penggunaan memory
- Gunakan numpy untuk operasi vektor