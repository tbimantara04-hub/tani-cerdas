import time
import json
import os
import subprocess
import shutil

results_path = 'backend/benchmark_results.json'

print("⏳ Menunggu benchmark selesai hingga 100 query...")
while True:
    if os.path.exists(results_path):
        try:
            with open(results_path, 'r', encoding='utf-8') as f:
                d = json.load(f)
            if len(d) >= 100:
                print("✅ Benchmark mencapai 100 data! Memulai evaluasi (LLM Judge)...")
                break
        except Exception:
            pass
    time.sleep(15)

print("🚀 Menjalankan evaluator.py (ini bisa memakan waktu 5-10 menit untuk judging)...")
subprocess.run([r"backend\venv\Scripts\python.exe", "backend/evaluator.py"])

print("📝 Menjalankan export_csv.py...")
subprocess.run([r"backend\venv\Scripts\python.exe", "backend/export_csv.py"])

onedrive_path = r"c:\Users\garra\OneDrive\Dokumen\SEMESTER 5\Conference\tani-cerda\evaluation_results.csv"
scratch_csv = "backend/evaluation_results.csv"

if os.path.exists(scratch_csv):
    try:
        os.makedirs(os.path.dirname(onedrive_path), exist_ok=True)
        shutil.copy2(scratch_csv, onedrive_path)
        print("📂 File final berhasil dicopy otomatis ke OneDrive Anda: " + onedrive_path)
    except Exception as e:
        print("Gagal copy ke onedrive:", e)
else:
    print("❌ File CSV hasil evaluasi tidak ditemukan di scratch pad!")
print("🎉 Selesai otomatis!")
