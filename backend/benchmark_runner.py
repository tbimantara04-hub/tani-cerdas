import json
import time
import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Ensure backend dir is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()
github_token = os.getenv("GITHUB_TOKEN")

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=github_token
)

from rag_logic import (
    ask_chatbot, 
    tanya_panduan_hama, 
    cek_cuaca, 
    cek_harga_pangan, 
    cek_harga_pupuk
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

# 1. Standard RAG (Only Vector DB via tanya_panduan_hama)
def run_standard_rag(query):
    try:
        return tanya_panduan_hama(query)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error in Standard RAG: {repr(e)}"

# 2. Static Multi-tool (Call all tools and ask LLM to synthesize)
def run_static_multi_tool(query):
    try:
        hama_res = tanya_panduan_hama(query)
        cuaca_res = cek_cuaca("")
        harga_pangan_res = cek_harga_pangan("")
        harga_pupuk_res = cek_harga_pupuk("")
        
        context = f"""
        [KONTEKS PANDUAN PERTANIAN]: {hama_res}
        [KONTEKS CUACA]: {cuaca_res}
        [KONTEKS HARGA PASAR]: {harga_pangan_res}
        [KONTEKS HARGA PUPUK]: {harga_pupuk_res}
        """
        
        prompt_text = f"""Anda adalah asisten Tani-Cerdas. Jawab pertanyaan pengguna berdasarkan KONTEKS.
        
KONTEKS:
{context}

PERTANYAAN: {query}

JAWABAN (Bahasa Indonesia):"""
        
        return call_github_model_api(prompt_text)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error in Static Multi-tool: {repr(e)}"

# 3. Agentic RAG (Live system using keyword-based tool selection)
def run_agentic_rag(query):
    try:
        return ask_chatbot(query, llm_mode="api")  # Use the GitHub Models API mode
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error in Agentic RAG: {repr(e)}", []

def main():
    dataset_path = "backend/evaluation_dataset.json"
    results_path = "backend/benchmark_results.json"
    
    if not os.path.exists(dataset_path):
        print(f"Dataset not found at {dataset_path}")
        return

    with open(dataset_path, "r", encoding="utf8") as f:
        dataset = json.load(f)

    # Load existing results to resume
    results = []
    if os.path.exists(results_path):
        with open(results_path, "r", encoding="utf8") as f:
            try:
                results = json.load(f)
            except json.JSONDecodeError:
                results = []

    start_idx = len(results)
    total = len(dataset)
    print(f"===== BENCHMARK START =====")
    print(f"Resuming from index {start_idx} out of {total}")
    print(f"Estimated time: ~{(total - start_idx) * 1.5:.0f} minutes")
    print(f"===========================")

    for i in range(start_idx, total):
        item = dataset[i]
        query = item['query']
        print(f"\n[{i+1}/{total}] Processing: {query[:60]}...")
        
        row = {
            "query": query,
            "category": item.get('category', 'Unknown'),
            "ground_truth": item['ideal_answer'],
            "expected_tools": item['expected_tools']
        }
        
        # 1. Standard RAG
        print(f"  -> Standard RAG...")
        t0 = time.time()
        row["standard_rag"] = run_standard_rag(query)
        row["standard_rag_time"] = time.time() - t0
        is_ok = "OK" if not row["standard_rag"].startswith("Error") else "FAIL"
        print(f"     {is_ok} ({row['standard_rag_time']:.1f}s)")
        
        # Wait between methods to respect rate limit
        time.sleep(2)
        
        # 2. Static Multi-tool
        print(f"  -> Static Multi-tool...")
        t0 = time.time()
        row["static_multi_tool"] = run_static_multi_tool(query)
        row["static_multi_tool_time"] = time.time() - t0
        is_ok = "OK" if not row["static_multi_tool"].startswith("Error") else "FAIL"
        print(f"     {is_ok} ({row['static_multi_tool_time']:.1f}s)")
        
        # Wait between methods
        time.sleep(2)
        
        # 3. Agentic RAG
        print(f"  -> Agentic RAG...")
        t0 = time.time()
        agent_result = run_agentic_rag(query)
        if isinstance(agent_result, tuple):
            agent_ans, tools_used = agent_result
        else:
            agent_ans = str(agent_result)
            tools_used = []
        row["agentic_rag"] = agent_ans
        row["agentic_rag_time"] = time.time() - t0
        row["agentic_rag_tools"] = tools_used
        is_ok = "OK" if not row["agentic_rag"].startswith("Error") else "FAIL"
        print(f"     {is_ok} ({row['agentic_rag_time']:.1f}s) tools={tools_used}")
        
        results.append(row)
        
        # Save after each query
        with open(results_path, "w", encoding="utf8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
            
        print(f"  -> Saved. Waiting 3s before next query...")
        time.sleep(3)
            
    print(f"\n===== BENCHMARK COMPLETE =====")
    print(f"Total: {len(results)} queries processed")
    print(f"Results saved to {results_path}")

if __name__ == "__main__":
    main()
