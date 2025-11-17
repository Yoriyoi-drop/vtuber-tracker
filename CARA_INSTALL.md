# Panduan Instalasi VTuber Tracker

## Panduan ini berisi langkah-langkah instalasi VTuber Tracker untuk sistem operasi Windows, macOS, dan Linux dalam bahasa Indonesia.

## Untuk Pemula
Jika Anda baru mengenal program ini atau teknologi komputer, ikuti langkah-langkah berikut dengan teliti. Jangan khawatir jika terdapat istilah-istilah yang belum Anda ketahui, panduan ini akan menjelaskan semuanya secara bertahap.

---

## Instalasi di Windows

### Langkah 1: Instal Python
1. Kunjungi situs web resmi Python: https://www.python.org/
2. Klik tombol "Download Python" (versi terbaru)
3. Saat proses instalasi berlangsung, **pastikan centang "Add Python to PATH"** (ini sangat penting!)
4. Klik "Install Now" untuk instalasi standar
5. Tunggu proses instalasi selesai

### Langkah 2: Verifikasi Instalasi Python
1. Tekan tombol `Windows + R` di keyboard Anda
2. Ketik `cmd` dan tekan Enter (ini akan membuka Command Prompt)
3. Ketik perintah berikut dan tekan Enter:
   ```
   python --version
   ```
4. Jika instalasi berhasil, akan muncul versi Python yang terinstal (misalnya: Python 3.10.0)

### Langkah 3: Unduh Kode Program
1. Buka browser Anda dan kunjungi halaman GitHub VTuber Tracker
2. Klik tombol "Code" dan pilih "Download ZIP"
3. Ekstrak file ZIP ke folder yang mudah diakses (misalnya ke Desktop)

### Langkah 4: Buka Command Prompt di Lokasi Program
1. Buka File Explorer dan navigasi ke folder hasil ekstrak
2. Klik kanan di dalam folder tersebut sambil menahan tombol Shift
3. Pilih "Open PowerShell window here" atau "Open command window here"

### Langkah 5: Instal Dependen Program
1. Di jendela Command Prompt / PowerShell, ketik perintah berikut dan tekan Enter:
   ```
   pip install opencv-python mediapipe pyqt5 python-osc websocket-client requests numpy pyfakewebcam
   ```
2. Tunggu proses instalasi selesai (ini bisa memakan waktu beberapa menit)

### Langkah 6: Jalankan Program
1. Dalam Command Prompt di folder program, ketik:
   ```
   python run_app.py
   ```
2. Program sekarang harus berjalan dan menampilkan antarmuka pengguna

---

## Instalasi di macOS

### Langkah 1: Instal Python
1. Kunjungi situs web resmi Python: https://www.python.org/
2. Klik tombol "Download Python" (versi terbaru)
3. Ikuti proses instalasi seperti biasa, ikuti petunjuk pada layar

### Langkah 2: Verifikasi Instalasi Python
1. Buka aplikasi "Terminal" (bisa ditemukan di folder Utilities)
2. Ketik perintah berikut dan tekan Enter:
   ```
   python3 --version
   ```
3. Jika instalasi berhasil, akan muncul versi Python yang terinstal

### Langkah 3: Unduh Kode Program
1. Buka browser Anda dan kunjungi halaman GitHub VTuber Tracker
2. Klik tombol "Code" dan pilih "Download ZIP"
3. Ekstrak file ZIP ke folder yang mudah diakses (misalnya ke Desktop)

### Langkah 4: Buka Terminal di Lokasi Program
1. Buka Finder dan navigasi ke folder hasil ekstrak
2. Buka Terminal
3. Ketik perintah `cd ` (spasi setelah `cd`) kemudian tarik folder program ke jendela Terminal dan tekan Enter

### Langkah 5: Instal Dependen Program
1. Di jendela Terminal, ketik perintah berikut dan tekan Enter:
   ```
   pip3 install opencv-python mediapipe pyqt5 python-osc websocket-client requests numpy pyfakewebcam
   ```
2. Tunggu proses instalasi selesai (ini bisa memakan waktu beberapa menit)

### Langkah 6: Jalankan Program
1. Dalam Terminal di folder program, ketik:
   ```
   python3 run_app.py
   ```
2. Program sekarang harus berjalan dan menampilkan antarmuka pengguna

---

## Instalasi di Linux (Ubuntu/Debian)

### Langkah 1: Perbarui Sistem
1. Buka Terminal (Ctrl + Alt + T)
2. Ketik perintah berikut dan tekan Enter:
   ```
   sudo apt update
   ```

### Langkah 2: Instal Python
1. Di Terminal, ketik perintah berikut dan tekan Enter:
   ```
   sudo apt install python3 python3-pip
   ```
2. Jika diminta, ketik password Anda dan tekan Enter

### Langkah 3: Verifikasi Instalasi Python
1. Di Terminal, ketik perintah berikut dan tekan Enter:
   ```
   python3 --version
   ```
2. Jika instalasi berhasil, akan muncul versi Python yang terinstal

### Langkah 4: Instal Dependen Sistem
1. Di Terminal, ketik perintah berikut dan tekan Enter:
   ```
   sudo apt install python3-opencv python3-dev python3-setuptools
   ```

### Langkah 5: Unduh Kode Program
1. Buka browser Anda dan kunjungi halaman GitHub VTuber Tracker
2. Klik tombol "Code" dan pilih "Download ZIP"
3. Simpan file ZIP ke folder Downloads

### Langkah 6: Ekstrak dan Navigasi ke Folder Program
1. Di Terminal, ketik perintah berikut dan tekan Enter:
   ```
   cd ~/Downloads
   unzip nama_file_program.zip  # ganti nama_file_program.zip dengan nama sebenarnya
   cd nama_folder_program       # ganti nama_folder_program dengan nama sebenarnya
   ```

### Langkah 7: Instal Dependen Program
1. Di Terminal, ketik perintah berikut dan tekan Enter:
   ```
   pip3 install opencv-python mediapipe pyqt5 python-osc websocket-client requests numpy pyfakewebcam
   ```
2. Tunggu proses instalasi selesai (ini bisa memakan waktu beberapa menit)

### Langkah 8: Jalankan Program
1. Dalam Terminal di folder program, ketik:
   ```
   python3 run_app.py
   ```
2. Program sekarang harus berjalan dan menampilkan antarmuka pengguna

### Catatan Khusus Linux:
- Jika Anda mendapatkan kesalahan permisi kamera, tambahkan user Anda ke grup video:
  ```
  sudo usermod -a -G video $USER
  ```
  Anda perlu login-ulang agar perubahan ini berlaku.

---

## Solusi Masalah Umum (Troubleshooting)

### 1. Kesalahan saat instalasi pip
Jika Anda mendapatkan kesalahan saat menjalankan perintah pip, coba instal dengan opsi `--user`:
```
pip install --user opencv-python mediapipe pyqt5 python-osc websocket-client requests numpy pyfakewebcam
```

### 2. Kamera tidak terdeteksi
- Pastikan kamera tidak digunakan oleh program lain
- Di Windows: Buka "Settings" > "Privacy" > "Camera" dan pastikan akses kamera diizinkan
- Di Linux: Pastikan Anda telah menambahkan user ke grup video

### 3. Program tidak berjalan
- Pastikan versi Python minimal 3.8
- Pastikan semua dependensi terinstal dengan benar
- Jalankan dari folder yang benar (tempat file run_app.py berada)

### 4. Kesalahan permission di Linux
Jika Anda mendapatkan kesalahan permission saat instalasi pip, gunakan perintah:
```
pip3 install --user opencv-python mediapipe pyqt5 python-osc websocket-client requests numpy pyfakewebcam
```

---

## Panduan Dasar Penggunaan

Setelah program berhasil berjalan:

1. Antarmuka pengguna (GUI) akan terbuka
2. Kamera akan aktif secara otomatis (pastikan izin kamera diberikan)
3. Untuk kalibrasi posisi netral: Klik tombol "Kalibrasi" saat wajah Anda berada dalam posisi netral
4. Gunakan slider untuk mengatur sensitivitas sesuai kebutuhan
5. Untuk output ke perangkat lunak lain (seperti VSeeFace), aktifkan opsi VMC output

## Dukungan
Jika Anda menemui masalah atau memiliki pertanyaan, silakan periksa file README.md atau buka isu di repository GitHub.