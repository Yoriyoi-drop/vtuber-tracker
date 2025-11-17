# Panduan Kontribusi

Terima kasih atas ketertarikan Anda dalam berkontribusi pada proyek VTuber Tracker! Panduan ini akan membantu Anda memahami bagaimana berkontribusi pada proyek ini.

## Cara Berkontribusi

### 1. Melaporkan Masalah (Issues)

Jika Anda menemukan bug atau memiliki ide untuk fitur baru, silakan buat GitHub issue dengan format berikut:

- **Bug Report**: Sertakan versi yang digunakan, sistem operasi, langkah-langkah yang menyebabkan bug, dan hasil yang diharapkan
- **Feature Request**: Jelaskan fitur yang diinginkan dan mengapa fitur ini penting

### 2. Pengembangan Fitur dan Perbaikan Bug

1. Fork repositori ini
2. Buat branch baru: `git checkout -b fitur/nama-fitur` atau `git checkout -b fix/nama-fix`
3. Lakukan perubahan Anda
4. Pastikan semua test masih berjalan
5. Commit perubahan Anda: `git commit -m 'Tambah fitur: deskripsi singkat'`
6. Push ke branch Anda: `git push origin fitur/nama-fitur`
7. Buat Pull Request

### 3. Gaya Penulisan Kode

- Gunakan Python style guide (PEP 8)
- Gunakan type hints di mana memungkinkan
- Gunakan docstrings di semua fungsi publik

### 4. Struktur Proyek

```
vtuber-tracker/
├── app.py              # Aplikasi utama
├── run_app.py          # Entry point untuk aplikasi
├── vtuber_tracker_lib.py  # Library utama
├── config/             # File konfigurasi
├── tracker/            # Modul pelacakan wajah
│   ├── face_tracking.py
│   ├── calibration.py
│   ├── smoothing.py
│   └── ...
├── sender/             # Modul pengiriman data
│   ├── vmc_sender.py
│   └── vts_sender.py
├── gui/                # Modul GUI
└── ...
```

### 5. Testing

- Pastikan menulis unit test untuk setiap fitur baru
- Jalankan semua test sebelum membuat pull request:
  ```bash
  python -m pytest
  ```

## Jenis Kontribusi yang Diperlukan

- Bug fixes
- Penambahan fitur
- Penulisan dokumentasi
- Penambahan test case
- Perbaikan performansi
- Pemindahan ke arsitektur plugin