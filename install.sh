#!/bin/bash
# Instalasi Otomatis VTuber Tracker
# File: install.sh
# Deskripsi: Skrip instalasi otomatis untuk VTuber Tracker

set -e  # Hentikan eksekusi jika ada error

echo "==========================================="
echo "VTuber Tracker - Instalasi Otomatis"
echo "==========================================="

# Cek apakah Python tersedia
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 tidak ditemukan. Pastikan Python3 terinstall."
    exit 1
fi

# Cek apakah pip tersedia
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 tidak ditemukan. Sedang menginstal pip3..."
    sudo apt update && sudo apt install python3-pip -y 2>/dev/null || echo "❌ Gagal menginstal pip3. Cek sistem Anda."
    if ! command -v pip3 &> /dev/null; then
        exit 1
    fi
fi

echo "✅ Python3 dan pip3 ditemukan"

# Instal dependencies sistem (untuk Ubuntu/Debian)
echo "📦 Menginstal dependencies sistem..."
sudo apt update 2>/dev/null || echo "Command not needed on non-Debian systems"
sudo apt install -y python3-opencv python3-dev build-essential pkg-config 2>/dev/null || echo "Skipping system package installation..."

# Instal dependencies Python
echo "📦 Menginstal dependencies Python..."
pip3 install opencv-python mediapipe pyqt5 python-osc websocket-client requests numpy pyfakewebcam pybind11 scipy

# Instal module sebagai package dengan mode editable (development)
echo "📦 Menginstal VTuber Tracker sebagai package..."
pip3 install -e .

# Cek apakah instalasi berhasil
if python3 -c "import main; print('✅ VTuber Tracker berhasil diinstal')" 2>/dev/null; then
    echo "🎉 Instalasi berhasil!"
    echo ""
    echo "Cara menjalankan:"
    echo "  python3 main.py                    # GUI mode"
    echo "  python3 main.py --mode cli         # CLI mode"
    echo "  vtuber-tracker                     # Alternatif command line"
    echo ""
    echo "Aplikasi siap digunakan tanpa harus aktifkan virtual environment!"
else
    echo "❌ Gagal menguji instalasi"
    exit 1
fi

echo "==========================================="
echo "Instalasi selesai! Selamat menggunakan VTuber Tracker!"
echo "==========================================="