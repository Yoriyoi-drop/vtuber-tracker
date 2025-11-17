#!/usr/bin/env python3
"""
VTuber Tracker - Main Entry Point
===============================

Ini adalah file utama yang menjadi titik masuk tunggal untuk aplikasi VTuber Tracker.
File ini memungkinkan pengguna untuk menjalankan aplikasi hanya dengan perintah:
`python main.py`

Author: Fajar
License: MIT
"""

import sys
import os
import argparse
import logging
import subprocess
import platform

# Tambahkan root proyek ke path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def check_dependencies():
    """
    Periksa apakah dependencies utama tersedia
    """
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
        print(f"Module yang hilang: {', '.join(missing_modules)}")
        print("\nUntuk menginstall dependencies secara otomatis:")
        print("  pip install opencv-python mediapipe numpy PyQt5 python-osc websocket-client requests pyfakewebcam")
        return False
    
    return True

def setup_logging():
    """
    Setup logging configuration
    """
    log_level = logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('vtuber_tracker_main.log'),
            logging.StreamHandler()
        ]
    )

def run_cli_mode(verbose=False):
    """
    Jalankan aplikasi dalam mode CLI
    """
    print("VTuber Tracker - CLI Mode")
    print("=" * 30)

    from run_app import main as run_app_main

    if verbose:
        sys.argv = ["run_app.py", "--mode", "cli", "--verbose"]
    else:
        sys.argv = ["run_app.py", "--mode", "cli"]

    run_app_main()

def run_gui_mode():
    """
    Jalankan aplikasi dalam mode GUI
    """
    print("VTuber Tracker - GUI Mode")
    print("=" * 30)
    
    from run_app import main as run_app_main
    sys.argv = ["run_app.py", "--mode", "gui"]  # Simulasikan argumen command line
    run_app_main()

def run_with_camera_index(camera_index):
    """
    Jalankan aplikasi dengan indeks kamera tertentu
    """
    print(f"VTuber Tracker - Using Camera Index: {camera_index}")
    print("=" * 50)
    
    from run_app import main as run_app_main
    sys.argv = ["run_app.py", "--mode", "gui", "--camera", str(camera_index)]
    run_app_main()

def run_with_android_camera(stream_url):
    """
    Jalankan aplikasi dengan kamera Android melalui IP Webcam
    """
    print(f"VTuber Tracker - Using Android Camera: {stream_url}")
    print("=" * 50)
    
    from run_app import main as run_app_main
    sys.argv = ["run_app.py", "--mode", "gui", "--stream-url", stream_url]
    run_app_main()

def print_help():
    """
    Cetak informasi bantuan
    """
    print("""
VTuber Tracker - All-in-One VTuber Solution
============================================

Cara penggunaan:
  python main.py [opsi]

Opsi yang tersedia:
  --mode MODE           Mode aplikasi: 'gui' (default) atau 'cli'
  --camera INDEX        Indeks kamera untuk digunakan (default: 0)
  --stream-url URL      URL kamera Android/IP (misal: http://192.168.1.100:8080/video)
  --cli                 Jalankan dalam mode CLI (sama dengan --mode cli)
  --help, -h            Tampilkan bantuan ini

Contoh penggunaan:
  python main.py                    # Jalankan GUI dengan kamera default
  python main.py --mode cli         # Jalankan dalam mode CLI
  python main.py --camera 1         # Gunakan kamera dengan indeks 1
  python main.py --stream-url http://192.168.1.100:8080/video  # Gunakan kamera Android

Platform yang didukung:
  - Windows 10/11
  - macOS (Intel & Apple Silicon)
  - Linux (Ubuntu, Debian, Fedora, Arch, dll.)

Dukungan output:
  - VSeeFace (VMC Protocol)
  - VTube Studio (WebSocket)
  - Virtual Camera
  - OSC untuk berbagai aplikasi VTuber

Kompatibel dengan:
  - Live2D Cubism
  - VRM Models (VRoid Studio)
  - Semua platform streaming (Twitch, YouTube, Zoom, Discord, VRChat, dll.)
    """)

def main():
    """
    Fungsi utama untuk menjalankan aplikasi
    """
    parser = argparse.ArgumentParser(
        description='VTuber Tracker - All-in-One VTuber Solution',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh:
  python main.py                    # Jalankan GUI dengan kamera default
  python main.py --mode cli         # Jalankan dalam mode CLI
  python main.py --camera 1         # Gunakan kamera dengan indeks 1
  python main.py --stream-url http://192.168.1.100:8080/video  # Gunakan kamera Android
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['gui', 'cli'],
        default='gui',
        help='Mode aplikasi: GUI (default) atau CLI (command-line)'
    )
    
    parser.add_argument(
        '--camera',
        type=int,
        default=None,
        help='Indeks kamera untuk digunakan (default: otomatis)'
    )
    
    parser.add_argument(
        '--stream-url',
        type=str,
        default=None,
        help='URL stream kamera Android/IP (misal: http://192.168.1.100:8080/video)'
    )
    
    parser.add_argument(
        '--cli',
        action='store_true',
        help='Jalankan dalam mode CLI (sama dengan --mode cli)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Aktifkan output verbose'
    )

    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("VTuber Tracker - All-in-One VTuber Solution")
    print("============================================")
    print(f"Sistem: {platform.system()} {platform.machine()}")
    print(f"Python: {platform.python_version()}")
    print()
    
    # Cek dependencies
    if not check_dependencies():
        print("\n[PERINGATAN] Beberapa module hilang. Instal dependencies terlebih dahulu.")
        print("   Perintah instalasi: pip install opencv-python mediapipe numpy PyQt5 python-osc websocket-client requests pyfakewebcam")
        response = input("Lanjutkan tanpa pengecekan dependencies? (y/n): ")
        if response.lower() not in ['y', 'yes', 'ya']:
            return

    # Tentukan mode
    if args.cli:
        mode = 'cli'
    else:
        mode = args.mode

    # Jalankan aplikasi berdasarkan konfigurasi
    try:
        if args.stream_url:
            print(f"[CAM] Menggunakan kamera IP/Android: {args.stream_url}")
            run_with_android_camera(args.stream_url)
        elif args.camera is not None:
            print(f"[CAM] Menggunakan kamera dengan indeks: {args.camera}")
            run_with_camera_index(args.camera)
        elif mode == 'cli':
            print("[CLI] Menjalankan dalam mode CLI...")
            run_cli_mode(verbose=args.verbose)
        else:
            print("[GUI] Menjalankan dalam mode GUI...")
            run_gui_mode()

    except KeyboardInterrupt:
        print("\n\n[STOP] Aplikasi dihentikan oleh pengguna (Ctrl+C)")
        logger.info("Aplikasi dihentikan oleh pengguna")
    except Exception as e:
        print(f"\n[ERROR] Terjadi kesalahan: {e}")
        logger.error(f"Error saat menjalankan aplikasi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()