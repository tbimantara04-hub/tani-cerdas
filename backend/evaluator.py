import json
import os
import time
import requests
from dotenv import load_dotenv

# Load env
load_dotenv("backend/.env")
google_api_key = os.getenv("GOOGLE_API_KEY")

def call_gemini_rest(prompt, model="qwen2.5:14b", retries=3):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    for i in range(retries):
        try:
            response = requests.post(url, json=payload, timeout=120)
            if response.status_code == 200:
                res_json = response.json()
                if 'response' in res_json:
                    return res_json['response']
        except Exception as e:
            pass
        time.sleep(2)
    return "Error"

def get_llm_score(query, ideal, system_response):
    """Uses Gemini REST as a judge to score semantic accuracy (0-10)."""
    if not system_response or "Error" in system_response:
        return 0
    
    prompt = f"""
    Evaluasi jawaban Sistem AI dibandingkan dengan Ground Truth (Jawaban Ideal).
    
    PERTANYAAN: {query}
    GROUND TRUTH: {ideal}
    JAWABAN SISTEM: {system_response}
    
    TUGAS:
    Berikan skor dari 0 hingga 10 berdasarkan akurasi fakta dan kelengkapan informasi.
    0 = Benar-benar salah atau error.
    10 = Sempurna, mengandung semua informasi kunci dari Ground Truth.
    
    Format Output (HANYA ANGKA):
    Skor: [angka]
    """
    
    res_text = call_gemini_rest(prompt)
    import re
    match = re.search(r"Skor[: ]*(\d+)", res_text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 5

def calculate_tool_accuracy(expected, actual):
    if not expected: return 1.0
    if not actual: return 0.0
    expected_set = set(expected)
    actual_set = set(actual)
    intersection = expected_set.intersection(actual_set)
    return len(intersection) / len(expected_set)

def main():
    results_path = "backend/benchmark_results.json"
    eval_path = "backend/evaluation_metrics.json"
    
    if not os.path.exists(results_path):
        print("Benchmark results not found.")
        return

    with open(results_path, "r", encoding="utf8") as f:
        data = json.load(f)

    print(f"Evaluating {len(data)} results using REST API Judge...")
    evaluated_data = []
    
    for i, row in enumerate(data):
        print(f"[{i+1}/{len(data)}] Scoring: {row['query'][:20]}...")
        row["agentic_score"] = get_llm_score(row["query"], row["ground_truth"], row["agentic_rag"])
        row["agentic_tool_acc"] = calculate_tool_accuracy(row["expected_tools"], row.get("agentic_rag_tools", []))
        row["standard_score"] = get_llm_score(row["query"], row["ground_truth"], row["standard_rag"])
        row["static_score"] = get_llm_score(row["query"], row["ground_truth"], row["static_multi_tool"])
        evaluated_data.append(row)
        time.sleep(1)

    with open(eval_path, "w", encoding="utf8") as f:
        json.dump(evaluated_data, f, indent=2, ensure_ascii=False)
    print(f"Evaluation complete. Saved to {eval_path}")

if __name__ == "__main__":
    main()
