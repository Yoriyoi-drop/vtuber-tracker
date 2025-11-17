#!/usr/bin/env python3
"""
VTuber Tracker - All-in-One VTuber Solution
=========================================

INI ADALAH APLIKASI UTAMA YANG BISA DIJALANKAN LANGSUNG TANPA HARUS AKTIFKAN VIRTUAL ENVIRONMENT!
================================================================================================

Cara penggunaan (hanya satu perintah ini saja):
  python run_vtuber_tracker.py            # GUI mode (default)
  python run_vtuber_tracker.py --mode cli # CLI mode
  python run_vtuber_tracker.py --help     # Tampilkan semua opsi

CATATAN PENTING:
- File ini akan otomatis mencari dan menggunakan virtual environment jika ada
- Jika virtual environment tidak ditemukan, akan mencari dependencies di sistem
- Ini adalah versi portable dari VTuber Tracker yang siap digunakan di mana saja
"""

import os
import sys
import subprocess
import importlib.util
import platform
import logging

def setup_logging():
    """Setup logging untuk aplikasi utama"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('vtuber_tracker_launcher.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

def find_virtual_environment():
    """Temukan virtual environment di direktori sekitar"""
    possible_paths = [
        './vtuber_env/bin/python',  # Path utama
        './vtuber_env/Scripts/python.exe',  # Windows
        './venv/bin/python',       # Nama alternatif
        './venv/Scripts/python.exe',  # Windows
        './env/bin/python',        # Nama lain
        './env/Scripts/python.exe',   # Windows
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            venv_dir = os.path.dirname(os.path.dirname(path))
            logger.info(f"Ditemukan virtual environment: {venv_dir}")
            return venv_dir
    return None

def check_dependencies():
    """Cek apakah dependencies utama tersedia"""
    required_modules = [
        ('cv2', 'opencv-python'),
        ('mediapipe', 'mediapipe'), 
        ('numpy', 'numpy'),
        ('PyQt5', 'PyQt5'),
        ('pythonosc', 'python-osc'),
        ('requests', 'requests'),
        ('pyfakewebcam', 'pyfakewebcam')
    ]
    
    missing = []
    for module_name, package_name in required_modules:
        try:
            importlib.util.find_spec(module_name)
        except (ImportError, AttributeError, ValueError):
            missing.append((module_name, package_name))
    
    if missing:
        logger.warning("Modules yang hilang:")
        for module, package in missing:
            logger.warning(f"  - {module} (install dengan: pip install {package})")
        return False
    return True

def get_project_root():
    """Dapatkan path root proyek"""
    return os.path.dirname(os.path.abspath(__file__))

def run_with_venv(venv_path, args):
    """Jalankan aplikasi dengan virtual environment"""
    if platform.system() == "Windows":
        python_executable = os.path.join(venv_path, "Scripts", "python.exe")
    else:
        python_executable = os.path.join(venv_path, "bin", "python")
    
    if not os.path.exists(python_executable):
        logger.error(f"Python executable tidak ditemukan: {python_executable}")
        return False
    
    # Siapkan command untuk menjalankan main.py
    cmd = [python_executable, "main.py"] + args
    
    try:
        result = subprocess.run(cmd)
        return result.returncode
    except KeyboardInterrupt:
        logger.info("Dihentikan oleh pengguna")
        return 130  # SIGINT
    except Exception as e:
        logger.error(f"Error menjalankan aplikasi: {e}")
        return 1

def run_with_system_python(args):
    """Jalankan aplikasi dengan Python sistem"""
    # Tambahkan path proyek ke sys.path
    project_root = get_project_root()
    sys.path.insert(0, project_root)
    
    # Coba import dan jalankan fungsi main dari main.py
    try:
        # Coba import main module
        spec = importlib.util.spec_from_file_location("main", os.path.join(project_root, "main.py"))
        main_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_module)
        
        # Ganti sys.argv untuk argumen yang benar
        original_argv = sys.argv[:]
        sys.argv = ["main.py"] + args
        
        # Jalankan fungsi main
        exit_code = main_module.main()
        
        # Kembalikan sys.argv ke kondisi semula
        sys.argv = original_argv
        
        return exit_code if isinstance(exit_code, int) else 0
    except Exception as e:
        logger.error(f"Error saat menjalankan aplikasi: {e}")
        import traceback
        traceback.print_exc()
        return 1

def main():
    """Fungsi utama untuk menjalankan VTuber Tracker"""
    print("")
    print("="*60)
    print("VTuber Tracker - All-in-One VTuber Solution")
    print("Siap pakai tanpa harus aktifkan virtual environment!")
    print("="*60)
    print(f"Python: {platform.python_version()}")
    print(f"Sistem: {platform.system()} {platform.machine()}")
    print(f"Direktori kerja: {os.getcwd()}")
    print("")
    
    # Simpan argumen yang diteruskan
    args = sys.argv[1:]  # Hilangkan nama script sendiri
    
    # Cek virtual environment
    venv_path = find_virtual_environment()
    
    if venv_path:
        logger.info(f"Menggunakan virtual environment: {venv_path}")
        return run_with_venv(venv_path, args)
    else:
        logger.info("Virtual environment tidak ditemukan, mencoba menggunakan sistem Python...")
        
        # Cek dependencies
        if not check_dependencies():
            print("\n❌ Dependencies tidak lengkap!")
            print("\nUntuk menginstall semua dependencies:")
            print("  pip install opencv-python mediapipe pyqt5 python-osc websocket-client requests numpy pyfakewebcam")
            print("\nATAU aktifkan virtual environment:")
            print("  source vtuber_env/bin/activate  # Linux/Mac")
            print("  vtuber_env\\Scripts\\activate   # Windows")
            return 1
        
        logger.info("Dependencies ditemukan, menjalankan aplikasi...")
        return run_with_system_python(args)

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)