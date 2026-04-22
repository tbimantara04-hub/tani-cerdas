import json
import os

def summarize():
    file_path = 'backend/evaluation_metrics.json'
    if not os.path.exists(file_path):
        print("File metrics tidak ditemukan.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not data:
        print("Data metrics kosong.")
        return

    stats = {
        'standard': {'scores': [], 'time': []},
        'static': {'scores': [], 'time': []},
        'agentic': {'scores': [], 'time': [], 'tool_acc': []}
    }

    for r in data:
        stats['standard']['scores'].append(r.get('standard_score', 0))
        stats['standard']['time'].append(r.get('standard_rag_time', 0))
        
        stats['static']['scores'].append(r.get('static_score', 0))
        stats['static']['time'].append(r.get('static_multi_tool_time', 0))
        
        stats['agentic']['scores'].append(r.get('agentic_score', 0))
        stats['agentic']['time'].append(r.get('agentic_rag_time', 0))
        stats['agentic']['tool_acc'].append(r.get('agentic_tool_acc', 0))

    def avg(lst):
        return sum(lst) / len(lst) if lst else 0

    print('| Metrik | Standard RAG | Static Multi-tool | Agentic RAG |')
    print('| :--- | :---: | :---: | :---: |')
    print(f'| **Rata-rata Skor (0-10)** | {avg(stats["standard"]["scores"]):.2f} | {avg(stats["static"]["scores"]):.2f} | {avg(stats["agentic"]["scores"]):.2f} |')
    print(f'| **Rata-rata Latensi** | {avg(stats["standard"]["time"]):.2f}s | {avg(stats["static"]["time"]):.2f}s | {avg(stats["agentic"]["time"]):.2f}s |')
    print(f'| **Akurasi Tool** | N/A | 100% (Static) | {avg(stats["agentic"]["tool_acc"])*100:.1f}% |')

if __name__ == "__main__":
    summarize()
