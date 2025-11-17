@echo off
REM Instalasi Otomatis VTuber Tracker (Windows)
REM File: install.bat
REM Deskripsi: Skrip instalasi otomatis untuk VTuber Tracker di Windows

echo ===========================================
echo VTuber Tracker - Instalasi Otomatis (Windows)
echo ===========================================

REM Cek apakah Python tersedia
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python tidak ditemukan. Pastikan Python3 terinstall dan ada di PATH.
    pause
    exit /b 1
)

REM Cek apakah pip tersedia
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip tidak ditemukan. Sedang menginstal pip...
    python -m ensurepip --upgrade
    if errorlevel 1 (
        echo ❌ Gagal menginstal pip. Cek instalasi Python Anda.
        pause
        exit /b 1
    )
)

echo ✅ Python dan pip ditemukan

REM Instal dependencies Python
echo 📦 Menginstal dependencies Python...
pip install opencv-python mediapipe pyqt5 python-osc websocket-client requests numpy pyfakewebcam pybind11 scipy

REM Instal module sebagai package dengan mode editable (development)
echo 📦 Menginstal VTuber Tracker sebagai package...
pip install -e .

REM Cek apakah instalasi berhasil
python -c "import main; print('✅ VTuber Tracker berhasil diinstal')" >nul 2>&1
if errorlevel 1 (
    echo ❌ Gagal menguji instalasi
    pause
    exit /b 1
)

echo 🎉 Instalasi berhasil!
echo.
echo Cara menjalankan:
echo   python main.py                    ^<- GUI mode
echo   python main.py --mode cli         ^<- CLI mode
echo   vtuber-tracker                   ^<- Alternatif command line
echo.
echo Aplikasi siap digunakan tanpa harus aktifkan virtual environment!
echo ===========================================
echo Instalasi selesai! Selamat menggunakan VTuber Tracker!
echo ===========================================
pause