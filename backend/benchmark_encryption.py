import time
import json
import os
import sys

# Tambahkan path agar bisa import security.py jika dijalankan dari dalam folder backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from security import encryptor

def benchmark():
    # Data sampel: 10 catatan penanaman
    data = [
        {
            "id": i, 
            "plant": "Padi", 
            "luas": "1000m2", 
            "date": "2024-03-26", 
            "notes": "Catatan rahasia petani nomor " + str(i)
        }
        for i in range(10)
    ]
    
    iterations = 100
    test_file_plain = "storage/test_plain.json"
    test_file_enc = "storage/test_enc.json"
    
    # Pastikan folder storage ada
    os.makedirs("storage", exist_ok=True)
    
    print("=" * 50)
    print(f"BENCHMARK PERFORMA TANI-CERDAS ({iterations} Iterasi)")
    print("=" * 50)
    
    # 1. Tanpa Enkripsi (JSON Biasa)
    print("\n[1] Menjalankan ujin tanpa enkripsi...")
    start_time = time.time()
    for _ in range(iterations):
        # Tulis ke disk
        with open(test_file_plain, "w") as f:
            f.write(json.dumps(data))
        # Baca dari disk
        with open(test_file_plain, "r") as f:
            _ = json.loads(f.read())
    end_time = time.time()
    plain_duration = (end_time - start_time) * 1000 / iterations
    print(f"Hasil: {plain_duration:.4f} ms per siklus (Tulis + Baca)")
    
    # 2. Dengan AES-256 Encryption (Fernet)
    print("\n[2] Menjalankan uji dengan AES-256...")
    start_time = time.time()
    for _ in range(iterations):
        # Enkripsi + Tulis
        json_str = json.dumps(data)
        enc_data = encryptor.encrypt(json_str)
        with open(test_file_enc, "w") as f:
            f.write(enc_data)
        # Baca + Dekripsi
        with open(test_file_enc, "r") as f:
            read_data = f.read()
            _ = json.loads(encryptor.decrypt(read_data))
    end_time = time.time()
    enc_duration = (end_time - start_time) * 1000 / iterations
    print(f"Hasil: {enc_duration:.4f} ms per siklus (Enkripsi + Tulis + Baca + Dekripsi)")
    
    # ANALISIS
    print("\n" + "=" * 50)
    print("KESIMPULAN ANALISIS")
    print("=" * 50)
    diff = enc_duration - plain_duration
    print(f"Selisih Waktu (Overhead): {diff:.4f} ms")
    
    if diff < 10:
        print("💡 STATUS: SANGAT EFISIEN")
        print("Enkripsi hanya menambah < 10ms. Ini tidak akan terasa oleh mata manusia.")
    else:
        print("💡 STATUS: NORMAL")
    
    # Pembersihan file uji coba
    if os.path.exists(test_file_plain): os.remove(test_file_plain)
    if os.path.exists(test_file_enc): os.remove(test_file_enc)
    print("\nFile uji coba telah dibersihkan.")

if __name__ == "__main__":
    benchmark()
