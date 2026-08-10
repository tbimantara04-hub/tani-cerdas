import json
import os
import time
import re
from dotenv import load_dotenv
from openai import OpenAI

# Load env
load_dotenv("backend/.env")
github_token = os.getenv("GITHUB_TOKEN")

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=github_token
)

def call_github_model_api(prompt, model="gpt-4o-mini", retries=3):
    if not github_token:
        print("ERROR: GITHUB_TOKEN not found in .env")
        return "Error: GITHUB_TOKEN_MISSING"
        
    for i in range(retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error calling GitHub Model API (attempt {i+1}): {e}")
            time.sleep(2)
    return "Error"

def get_llm_score(query, ideal, system_response):
    """Uses GitHub Models API as a judge to score semantic accuracy (0-10)."""
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
    
    res_text = call_github_model_api(prompt)
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

    print(f"Evaluating {len(data)} results using GitHub Model API Judge...")
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
