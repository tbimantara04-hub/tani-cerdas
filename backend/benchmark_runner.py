import json
import time
import os
import sys

# Ensure backend dir is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_logic import (
    ask_chatbot, 
    tanya_panduan_hama, 
    cek_cuaca, 
    cek_harga_pangan, 
    cek_harga_pupuk,
    llm,
    call_gemini_rest
)

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. Standard RAG (Only Vector DB via tanya_panduan_hama)
def run_standard_rag(query):
    try:
        return tanya_panduan_hama.invoke(query)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error in Standard RAG: {repr(e)}"

# 2. Static Multi-tool (Call all tools and ask LLM to synthesize)
def run_static_multi_tool(query):
    try:
        hama_res = tanya_panduan_hama.invoke(query)
        cuaca_res = cek_cuaca.invoke("")
        harga_pangan_res = cek_harga_pangan.invoke("")
        harga_pupuk_res = cek_harga_pupuk.invoke("")
        
        context = f"""
        [KONTEKS PANDUAN PERTANIAN]: {hama_res}
        [KONTEKS CUACA]: {cuaca_res}
        [KONTEKS HARGA PASAR]: {harga_pangan_res}
        [KONTEKS HARGA PUPUK]: {harga_pupuk_res}
        """
        
        # Use direct REST call instead of chain to avoid extra overhead
        prompt_text = f"""Anda adalah asisten Tani-Cerdas. Jawab pertanyaan pengguna berdasarkan KONTEKS.
        
KONTEKS:
{context}

PERTANYAAN: {query}

JAWABAN (Bahasa Indonesia):"""
        
        return call_gemini_rest(prompt_text)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error in Static Multi-tool: {repr(e)}"

# 3. Agentic RAG (Live system using keyword-based tool selection)
def run_agentic_rag(query):
    try:
        return ask_chatbot(query)
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
            except:
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
        time.sleep(8)
        
        # 2. Static Multi-tool
        print(f"  -> Static Multi-tool...")
        t0 = time.time()
        row["static_multi_tool"] = run_static_multi_tool(query)
        row["static_multi_tool_time"] = time.time() - t0
        is_ok = "OK" if not row["static_multi_tool"].startswith("Error") else "FAIL"
        print(f"     {is_ok} ({row['static_multi_tool_time']:.1f}s)")
        
        # Wait between methods
        time.sleep(8)
        
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
            
        print(f"  -> Saved. Waiting 10s before next query...")
        time.sleep(10)
            
    print(f"\n===== BENCHMARK COMPLETE =====")
    print(f"Total: {len(results)} queries processed")
    print(f"Results saved to {results_path}")

if __name__ == "__main__":
    main()
