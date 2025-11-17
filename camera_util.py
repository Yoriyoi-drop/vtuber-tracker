"""
Utility untuk mendeteksi dan menguji kamera sebelum menggunakan VTuber Tracker
"""

import cv2
import sys

def detect_cameras():
    """Deteksi semua kamera yang tersedia dan informasi tentangnya."""
    print("Mendeteksi kamera yang tersedia...")
    print("=" * 50)
    
    cameras = []
    max_test_index = 10  # Test dari 0 sampai 9
    
    for i in range(max_test_index):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            # Coba baca frame untuk konfirmasi
            ret, frame = cap.read()
            if ret:
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                
                cameras.append({
                    'index': i,
                    'resolution': f"{width}x{height}",
                    'fps': fps,
                    'frame_shape': frame.shape if frame is not None else None
                })
                
                print(f"Kamera DITEMUKAN di indeks {i}")
                print(f"  - Resolusi: {width}x{height}")
                print(f"  - FPS: {fps}")
                if frame is not None:
                    print(f"  - Frame shape: {frame.shape}")
                print()
            cap.release()
        else:
            # Jika indeks pertama saja tidak bisa dibuka, mungkin tidak ada kamera
            if i == 0:
                print("⚠️  Tidak ada kamera yang terdeteksi!")
                print("Kemungkinan masalah:")
                print("  - Kamera tidak terhubung")
                print("  - Aplikasi lain sedang menggunakan kamera")
                print("  - Driver kamera belum terinstal")
                print("  - Hak akses sistem tidak mencukupi")
                break
            else:
                # Jika indeks pertama bisa dibuka tetapi indeks berikutnya tidak
                # kemungkinan tidak ada lagi kamera
                break
    
    if cameras:
        print(f"✅ Total kamera ditemukan: {len(cameras)}")
        print("Daftar kamera yang bisa digunakan:")
        for cam in cameras:
            print(f"  - Indeks: {cam['index']}, Resolusi: {cam['resolution']}")
        print()
    
    return cameras

def test_camera(index, duration=5):
    """
    Test kamera tertentu dengan menampilkan feed secara real-time.
    
    Args:
        index: Indeks kamera untuk diuji
        duration: Durasi dalam detik untuk menampilkan feed (0 untuk tak terbatas)
    """
    print(f"Testing kamera indeks {index} selama {duration} detik...")
    
    cap = cv2.VideoCapture(index)
    
    if not cap.isOpened():
        print(f"❌ Gagal membuka kamera indeks {index}")
        return False
    
    # Set property untuk kamera
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    print(f"✅ Kamera indeks {index} berhasil dibuka")
    print(f"   Resolusi: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
    
    import time
    start_time = time.time()
    frame_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Gagal membaca frame dari kamera")
                break
            
            # Tampilkan frame
            cv2.imshow(f'Test Kamera {index}', frame)
            frame_count += 1
            
            # Keluar jika menekan 'q' atau waktu habis
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or (duration > 0 and time.time() - start_time > duration):
                break
    
    except KeyboardInterrupt:
        print("\nTesting dihentikan oleh user")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
    
    fps = frame_count / (time.time() - start_time) if (time.time() - start_time) > 0 else 0
    print(f"✅ Testing selesai. Total frame: {frame_count}, FPS rata-rata: {fps:.2f}")
    return True

def get_camera_recommendation():
    """Dapatkan rekomendasi kamera terbaik untuk digunakan."""
    cameras = detect_cameras()
    
    if not cameras:
        return None
    
    # Pilih kamera dengan resolusi tertinggi sebagai default
    best_camera = max(cameras, key=lambda x: int(x['resolution'].split('x')[0]) * int(x['resolution'].split('x')[1]))
    
    print("Rekomendasi:")
    print(f"  Gunakan kamera indeks: {best_camera['index']}")
    print(f"  Dengan resolusi: {best_camera['resolution']}")
    
    return best_camera['index']

def main():
    """Fungsi utama untuk utility kamera."""
    print("VTuber Tracker - Kamera Detection Utility")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test" and len(sys.argv) > 2:
            # Test kamera spesifik: python camera_util.py test 0
            try:
                cam_index = int(sys.argv[2])
                duration = int(sys.argv[3]) if len(sys.argv) > 3 else 5
                test_camera(cam_index, duration)
            except ValueError:
                print("Gunakan: python camera_util.py test <index> [durasi_detik]")
        elif sys.argv[1] == "detect":
            # Deteksi semua kamera: python camera_util.py detect
            detect_cameras()
        else:
            print("Penggunaan:")
            print("  python camera_util.py detect     # Deteksi semua kamera")
            print("  python camera_util.py test <index> [durasi]  # Test kamera spesifik")
    else:
        # Default behavior: detect cameras and recommend best one
        get_camera_recommendation()

if __name__ == "__main__":
    main()