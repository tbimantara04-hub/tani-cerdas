import json
import csv
import os

def export_to_csv():
    json_path = 'backend/evaluation_metrics.json'
    csv_path = 'backend/evaluation_results.csv'
    
    if not os.path.exists(json_path):
        # Try benchmark_results.json if metrics doesn't exist
        json_path = 'backend/benchmark_results.json'
        
    if not os.path.exists(json_path):
        print(f"Error: {json_path} tidak ditemukan.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not data:
        print("Error: Data kosong.")
        return

    # Extract headers from the first item
    headers = list(data[0].keys())
    
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in data:
            # Flatten any lists (like expected_tools or agentic_rag_tools) if needed
            processed_row = {}
            for k, v in row.items():
                if isinstance(v, list):
                    processed_row[k] = ", ".join(map(str, v))
                else:
                    processed_row[k] = v
            writer.writerow(processed_row)

    print(f"Berhasil mengekspor evaluasi ke {csv_path}")

if __name__ == "__main__":
    export_to_csv()
