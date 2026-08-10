import json
import os
import sys

def colored(text, color):
    colors = {
        'blue': '\033[94m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'bold': '\033[1m',
        'end': '\033[0m'
    }
    return f"{colors.get(color, '')}{text}{colors['end']}"

def main():
    bench_file = 'backend/benchmark_results.json'
    eval_file = 'backend/evaluation_metrics.json'

    # Load benchmark data
    if not os.path.exists(bench_file):
        print(colored(f"Error: {bench_file} tidak ditemukan!", 'red'))
        return

    with open(bench_file, 'r', encoding='utf-8') as f:
        bench_data = json.load(f)

    # Load or initialize evaluation data
    eval_data = []
    if os.path.exists(eval_file):
        with open(eval_file, 'r', encoding='utf-8') as f:
            try:
                eval_data = json.load(f)
            except json.JSONDecodeError:
                eval_data = []

    start_idx = len(eval_data)
    total = len(bench_data)

    if start_idx >= total:
        print(colored("\n🎉 Semua query sudah dievaluasi! Yay!", 'green'))
        print(colored("Sekarang Anda bisa menjalankan: python backend/summarize_metrics.py\n", 'cyan'))
        return

    print(colored(f"\n🚀 Memulai CLI Evaluator... (Melanjutkan dari indeks {start_idx+1}/{total})", 'bold'))
    print(colored("Ketik 'q' atau 'quit' kapan saja untuk menyimpan progres dan keluar.\n", 'yellow'))

    for i in range(start_idx, total):
        item = bench_data[i]
        
        # Salin item untuk dievaluasi
        eval_item = item.copy()

        print("="*80)
        print(colored(f"📝 QUERY [{i+1}/{total}]:", 'cyan'), colored(item['query'], 'bold'))
        print(colored(f"Kategori    :", 'cyan'), item['category'])
        print(colored(f"Ground Truth:", 'green'), item['ground_truth'])
        print(colored(f"Exp. Tools  :", 'yellow'), item.get('expected_tools', []))
        print("="*80)

        # 1. EVALUASI STANDARD RAG
        print(colored("\n[1] STANDARD RAG", 'magenta'))
        print(f"Jawaban: {item.get('standard_rag', 'N/A')}")
        while True:
            val = input(colored(">>> Masukkan Skor Standard RAG (0-10) [q=keluar]: ", 'bold'))
            if val.lower() in ['q', 'quit']:
                print(colored("\n💾 Progres disimpan. Sampai jumpa!", 'yellow'))
                return
            try:
                score = float(val)
                if 0 <= score <= 10:
                    eval_item['standard_score'] = score
                    break
                print(colored("Skor harus antara 0 - 10!", 'red'))
            except ValueError:
                print(colored("Masukkan angka valid!", 'red'))

        # 2. EVALUASI STATIC MULTI-TOOL
        print(colored("\n[2] STATIC MULTI-TOOL", 'magenta'))
        print(f"Jawaban: {item.get('static_multi_tool', 'N/A')}")
        while True:
            val = input(colored(">>> Masukkan Skor Static Multi-Tool (0-10) [q=keluar]: ", 'bold'))
            if val.lower() in ['q', 'quit']:
                print(colored("\n💾 Progres disimpan. Sampai jumpa!", 'yellow'))
                return
            try:
                score = float(val)
                if 0 <= score <= 10:
                    eval_item['static_score'] = score
                    break
                print(colored("Skor harus antara 0 - 10!", 'red'))
            except ValueError:
                print(colored("Masukkan angka valid!", 'red'))

        # 3. EVALUASI AGENTIC RAG
        print(colored("\n[3] AGENTIC RAG", 'magenta'))
        print(f"Tools Used: {item.get('agentic_rag_tools', [])}")
        print(f"Jawaban   : {item.get('agentic_rag', 'N/A')}")
        while True:
            val = input(colored(">>> Masukkan Skor Agentic RAG (0-10) [q=keluar]: ", 'bold'))
            if val.lower() in ['q', 'quit']:
                print(colored("\n💾 Progres disimpan. Sampai jumpa!", 'yellow'))
                return
            try:
                score = float(val)
                if 0 <= score <= 10:
                    eval_item['agentic_score'] = score
                    break
                print(colored("Skor harus antara 0 - 10!", 'red'))
            except ValueError:
                print(colored("Masukkan angka valid!", 'red'))

        # 4. EVALUASI AGENTIC TOOL ACCURACY
        print(colored("\n[4] AKURASI TOOL AGENTIC", 'magenta'))
        print(f"Expected Tools: {item.get('expected_tools', [])}")
        print(f"Used Tools    : {item.get('agentic_rag_tools', [])}")
        while True:
            val = input(colored(">>> Apakah tool Agentic sesuai? (1=Ya, 0=Tidak) [q=keluar]: ", 'bold'))
            if val.lower() in ['q', 'quit']:
                print(colored("\n💾 Progres disimpan. Sampai jumpa!", 'yellow'))
                return
            try:
                acc = int(val)
                if acc in [0, 1]:
                    eval_item['agentic_tool_acc'] = acc
                    break
                print(colored("Masukkan angka 1 atau 0 saja!", 'red'))
            except ValueError:
                print(colored("Masukkan angka 1 atau 0!", 'red'))

        # Simpan hasil per iterasi
        eval_data.append(eval_item)
        with open(eval_file, 'w', encoding='utf-8') as f:
            json.dump(eval_data, f, indent=2, ensure_ascii=False)
        print(colored(f"\n✅ Data kueri ke-{i+1} tersimpan!\n", 'blue'))
    
    print(colored("🎉 Selesai! Semua query telah dievaluasi.", 'green'))
    print(colored("Jalankan 'python backend/summarize_metrics.py' untuk melihat hasil akhirnya.", 'cyan'))

if __name__ == '__main__':
    main()
