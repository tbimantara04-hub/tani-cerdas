import json, csv, os
import sys

sys.path.append('backend')
from evaluator import calculate_tool_accuracy

with open('backend/benchmark_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for row in data:
    row['agentic_tool_acc'] = calculate_tool_accuracy(row.get('expected_tools', []), row.get('agentic_rag_tools', []))
    row['agentic_score'] = 0 
    row['standard_score'] = 0
    row['static_score'] = 0

if data:
    headers = list(data[0].keys())
    scratch_csv = 'backend/evaluation_results_partial.csv'
    with open(scratch_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in data:
            pr = {}
            for k, v in row.items():
                if isinstance(v, list): pr[k] = ", ".join(map(str, v))
                else: pr[k] = v
            writer.writerow(pr)

    import shutil
    onedrive_path = r"c:\Users\garra\OneDrive\Dokumen\SEMESTER 5\Conference\tani-cerda\evaluation_results.csv"
    shutil.copy2(scratch_csv, onedrive_path)
    print("Partial CSV exported to OneDrive.")
