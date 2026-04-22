import os
import json
import time
import sys
from dotenv import load_dotenv

def log(msg):
    with open("backend/gen_debug.log", "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    print(msg)

try:
    log("Starting dataset generator...")
    load_dotenv("backend/.env")
    API_KEY = os.getenv("GOOGLE_API_KEY")
    if not API_KEY:
        log("ERROR: GOOGLE_API_KEY not found in .env")
        sys.exit(1)
        
    import google.generativeai as genai
    genai.configure(api_key=API_KEY)
    log("Google AI configured.")

    def generate_queries(category, count=20):
        prompt = f"""Buatkan dataset berisi {count} pertanyaan unik petani dalam bahasa Indonesia untuk AI asisten "Tani Cerdas".
Kategori: {category}

Format JSON (List of Objects):
[
  {{
    "category": "{category}",
    "query": "Pertanyaan teknis/pasar/cuaca yang natural dalam Bahasa Indonesia",
    "expected_tools": ["sesuaikan_dengan_kategori_contoh: cek_harga_pangan, cek_cuaca"],
    "ideal_answer": "Jawaban singkat dan padat dalam Bahasa Indonesia"
  }}
]

Berikan output HANYA JSON array tanpa teks penjelasan apapun."""

        model = genai.GenerativeModel('models/gemini-2.5-flash')
        try:
            log(f"Requesting {count} queries for {category}...")
            response = model.generate_content(prompt)
            content = response.text.strip()
            log(f"Received response for {category}. Length: {len(content)}")
            
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end != -1:
                json_str = content[start:end]
                data = json.loads(json_str)
                log(f"Parsed {len(data)} queries for {category}.")
                return data
            else:
                log(f"ERROR: No JSON array found in response for {category}")
                return []
        except Exception as e:
            log(f"ERROR in generate_queries for {category}: {e}")
            return []

    all_queries = []
    categories = ["Cuaca", "Harga Pasar", "Penyakit & Hama", "Kombinasi", "Profil Petani"]
    
    for cat in categories:
        batch = generate_queries(cat, count=20)
        if batch:
            all_queries.extend(batch)
            log(f"Added {len(batch)} to all_queries. Total: {len(all_queries)}")
        time.sleep(1)

    output_file = "backend/evaluation_dataset.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_queries, f, indent=2, ensure_ascii=False)
    log(f"Final dataset saved to {output_file}. Total queries: {len(all_queries)}")

except Exception as global_e:
    log(f"GLOBAL ERROR: {global_e}")
