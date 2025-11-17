#!/usr/bin/env python3
"""
VTuber Tracker - Application Launcher
====================================

Skrip ini berfungsi sebagai peluncur untuk VTuber Tracker tanpa harus
mengaktifkan virtual environment secara manual.
Skrip ini akan secara otomatis mengaktifkan virtual environment jika ada,
dan menjalankan aplikasi.
"""

import subprocess
import sys
import os
import shutil

def find_and_run_app():
    """
    Cari virtual environment dan jalankan aplikasi
    """
    print("VTuber Tracker - Automatic Launcher")
    print("=" * 40)
    
    # Cek apakah dalam virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if in_venv:
        # Sudah dalam virtual environment
        print("✅ Sudah dalam virtual environment")
    else:
        # Cari virtual environment
        venv_paths = [
            "./vtuber_env/bin/python",  # Common path
            "./venv/bin/python",        # Alternative path
            "./env/bin/python",         # Another alternative
        ]
        
        venv_python = None
        for path in venv_paths:
            if os.path.exists(path):
                venv_python = os.path.abspath(path)
                break
        
        if venv_python:
            print(f"✅ Virtual environment ditemukan: {os.path.dirname(os.path.dirname(venv_python))}")
            # Jalankan dengan virtual environment
            cmd = [venv_python, "main.py"] + sys.argv[1:]
            try:
                result = subprocess.run(cmd)
                sys.exit(result.returncode)
            except Exception as e:
                print(f"❌ Gagal menjalankan dengan virtual environment: {e}")
                sys.exit(1)
        else:
            print("⚠️  Virtual environment tidak ditemukan")
            print("   Mengasumsikan dependencies sudah terinstal secara global")
    
    # Jika tidak dalam venv atau venv tidak ditemukan, cek dependencies
    required_modules = [
        "cv2",      # OpenCV
        "mediapipe", # MediaPipe
        "numpy",    # NumPy
        "PyQt5",    # PyQt5
        "pythonosc" # python-osc
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Module yang hilang: {', '.join(missing_modules)}")
        print("\nSolusi:")
        print("  1. Buat virtual environment dan install dependencies:")
        print("     python -m venv vtuber_env")
        print("     source vtuber_env/bin/activate  # Linux/Mac")
        print("     vtuber_env\\Scripts\\activate   # Windows")
        print("     pip install -r requirements.txt")
        print("  2. Atau install dependencies ke sistem secara global")
        print("     pip install opencv-python mediapipe pyqt5 python-osc websocket-client requests numpy pyfakewebcam")
        sys.exit(1)
    
    # Jika dependencies OK, jalankan aplikasi utama
    print("✅ Dependencies ditemukan, menjalankan aplikasi...")
    
    # Tambahkan current directory ke path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # Import dan jalankan fungsi main dari main.py
    try:
        from main import main as app_main
        sys.exit(app_main())
    except ImportError as e:
        print(f"❌ Gagal mengimport main.py: {e}")
        print("   Pastikan berada di direktori proyek VTuber Tracker")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error saat menjalankan aplikasi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    find_and_run_app()