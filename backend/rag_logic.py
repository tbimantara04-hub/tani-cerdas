"""
rag_logic.py — Agentic RAG v2.5 (Qwen-Local Edition)
====================================================
Perubahan utama:
1. Cloud Models REMOVED  →  Local Qwen 1.5B (via Ollama)
2. Embeddings REMOVED     →  Local Ollama Embeddings (nomic-embed-text)
3. Native Tool Calling    →  Manual JSON-ReAct Loop (Optimized for 1.5B model)
4. Full Offline Support.
"""

import os
import json
import time
import requests
import threading
from dotenv import load_dotenv
from security import encryptor, verify_faiss_checksum, write_faiss_checksum

# ── LangChain imports ────────────────────────────────────────────────────────
from langchain_core.tools import tool
from langchain_core.runnables import RunnableLambda
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import glob
import re

def extract_json_objects(text):
    objs = []
    stack = []
    start_idx = -1
    for i, char in enumerate(text):
        if char == '{':
            if not stack:
                start_idx = i
            stack.append(char)
        elif char == '}':
            if stack:
                stack.pop()
                if not stack:
                    objs.append(text[start_idx:i+1])
    return objs

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
# Menggunakan GITHUB_TOKEN untuk model cloud (GitHub Models API)

# ============================================================
# LLM — Dynamic Selection (Ollama or GitHub Models API)
# ============================================================
def get_llm(llm_mode="local"):
    if llm_mode == "api":
        github_token = os.environ.get("GITHUB_TOKEN")
        if not github_token or github_token == "your_github_pat_here":
            raise ValueError("GITHUB_TOKEN_MISSING")
        return ChatOpenAI(
            model="gpt-4o-mini",
            api_key=github_token,
            base_url="https://models.inference.ai.azure.com",
            temperature=0.1
        )
    return ChatOllama(
        model="qwen2:1.5b",
        temperature=0.1,
        num_gpu=0,
    )

# Embedding lokal menggunakan nomic-embed-text (Ollama)
# Jika belum ada, pastikan jalankan: ollama pull nomic-embed-text
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# Configuration
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_FAISS_PATH = os.path.join(BASE_DIR, "vectorstore", "db_faiss_local")


def get_retriever():
    """Inisialisasi atau muat FAISS retriever lokal."""
    if not os.path.exists(DB_FAISS_PATH) or not verify_faiss_checksum(DB_FAISS_PATH):
        docs_all = []
        
        # Load PDF
        for pdf_file in glob.glob(os.path.join(DATA_DIR, "*.pdf")):
            docs_all.extend(PyPDFLoader(pdf_file).load())
            
        # Load DOCX
        for docx_file in glob.glob(os.path.join(DATA_DIR, "*.docx")):
            docs_all.extend(Docx2txtLoader(docx_file).load())
            
        # Fallback to root dir if not found in data dir
        if not docs_all and os.path.exists("panduan hama (exp).pdf"):
            docs_all.extend(PyPDFLoader("panduan hama (exp).pdf").load())
            
        if not docs_all:
            return None
            
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        texts = splitter.split_documents(docs_all)
        db = FAISS.from_documents(texts, embeddings)
        db.save_local(DB_FAISS_PATH)
        write_faiss_checksum(DB_FAISS_PATH)
    else:
        db = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
    return db.as_retriever(search_kwargs={"k": 5})


# ============================================================
# TOOLS — Definisi semua tool
# ============================================================

def tanya_panduan_hama(query: str = "pertanian umum") -> str:
    """Mencari jawaban tentang hama/teknik tani dari dokumen."""
    retriever = get_retriever()
    if not retriever: return "Panduan tidak tersedia."
    docs = retriever.invoke(query)
    context = "\n".join(doc.page_content for doc in docs)
    return f"Konteks dari Panduan:\n{context}"

def cek_harga_pangan(komoditas: str = "") -> str:
    """Mengecek harga pangan BAPANAS Apr 2026."""
    harga_data = {
        "beras": "Rp 13.500/kg", "cabai rawit": "Rp 48.000/kg",
        "bawang merah": "Rp 32.000/kg", "jagung": "Rp 5.500/kg"
    }
    k = komoditas.lower()
    for key, val in harga_data.items():
        if key in k: return f"Harga {key}: {val}."
    return f"Harga Pangan: {', '.join([f'{k}: {v}' for k, v in harga_data.items()])}"

def cek_harga_pupuk(jenis_pupuk: str = "") -> str:
    """HET Pupuk subsidi 2024."""
    return f"Harga Pupuk {jenis_pupuk}: Urea Rp 2.250/kg, NPK Rp 2.300/kg."

def cek_cuaca(lokasi: str = "") -> str:
    """Cek cuaca menggunakan OpenWeatherMap API."""
    if not lokasi:
        profile = ambil_profil_petani()
        if profile and isinstance(profile, dict) and profile.get("lokasi"):
            lokasi = profile.get("lokasi")
        else:
            lokasi = "Jakarta"
    try:
        api_key = os.environ.get("OPENWEATHER_API_KEY", "")
        url = f"https://api.openweathermap.org/data/2.5/weather?q={lokasi}&appid={api_key}&units=metric&lang=id"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            suhu = data['main']['temp']
            kondisi = data['weather'][0]['description']
            return f"Cuaca di {lokasi}: {kondisi}, suhu {suhu}°C."
        return "Data cuaca API sibuk."
    except requests.RequestException as e:
        print(f"[Weather API Error] {e}")
        return "Gagal cek cuaca karena masalah jaringan."
    except Exception as e:
        print(f"[Weather Error] {e}")
        return "Gagal cek cuaca."

def lihat_profil_petani() -> str:
    """Baca profil dari storage."""
    PROFILE_FILE = "storage/farmer_profile.json"
    if not os.path.exists(PROFILE_FILE): return "Profil kosong."
    try:
        with open(PROFILE_FILE, "r") as f:
            data = encryptor.decrypt(f.read())
            p = json.loads(data)
            return f"Profil: {p['tanaman']} di {p['lokasi']} ({p['luas_lahan']})"
    except Exception as e:
        print(f"[Profile Read Error] {e}")
        return "Gagal baca profil."

def simpan_profil_petani(tanaman: str, luas_lahan: str, lokasi: str = "") -> str:
    """Simpan profil ke storage."""
    try:
        p = {"tanaman": tanaman, "luas_lahan": luas_lahan, "lokasi": lokasi}
        os.makedirs("storage", exist_ok=True)
        with open("storage/farmer_profile.json", "w") as f:
            f.write(encryptor.encrypt(json.dumps(p)))
        return "Profil berhasil disimpan."
    except Exception as e:
        print(f"[Profile Save Error] {e}")
        return "Gagal simpan profil."

# Dispatcher untuk mempermudah pemanggilan manual
TOOL_DISPATCHER = {
    "tanya_panduan_hama": tanya_panduan_hama,
    "cek_harga_pangan": cek_harga_pangan,
    "cek_harga_pupuk": cek_harga_pupuk,
    "cek_cuaca": cek_cuaca
}

# ============================================================
# AGENTIC LOOP (Manual ReAct for 14B)
# ============================================================

SYSTEM_PROMPT = """Kamu adalah Tani-Cerdas, asisten AI lokal terbaik.
Kamu memiliki alat (tools) berikut untuk mengambil data:
1. tanya_panduan_hama(query)
2. cek_harga_pangan(komoditas)
3. cek_harga_pupuk(jenis_pupuk)
4. cek_cuaca(lokasi)

ATURAN BALASAN SANGAT KETAT:
- Jika kamu BISA langsung menjawab dari ingatan/konteks, BALAS dengan bahasa natural biasa. HANYA TULIS JAWABANMU SECARA LANGSUNG.
- JIKA DAN HANYA JIKA kamu BUTUH MENARIK DATA dari tool, BALAS HANYA DENGAN BLOK JSON tunggal berikut (tanpa ada teks lain, tanpa kata Thought):
{"action": "nama_tool", "action_input": {"nama_parameter": "nilai"}}"""

def ask_chatbot(query: str, llm_mode: str = "local"):
    profile = ambil_profil_petani()
    context_str = ""
    if profile:
        tanaman = profile.get("tanaman", "")
        luas_lahan = profile.get("luas_lahan", "")
        lokasi = profile.get("lokasi", "")
        context_str = f"Konteks Pengguna Aktif:\n- Tanaman: {tanaman}\n- Luas Lahan: {luas_lahan}\n- Lokasi: {lokasi}\n\n[INFO INTERNAL PENTING UNTUK AI]: Ingat selalu konteks pengguna di atas. Jika pengguna bertanya tentang 'lahan saya' atau 'tanaman saya', gunakan informasi tersebut untuk menjawab. Kamu dapat menggunakan tool lain untuk melengkapi jawaban jika perlu."

    system_content = SYSTEM_PROMPT
    if context_str:
        system_content += f"\n\n{context_str}"

    messages = [
        SystemMessage(content=system_content),
        HumanMessage(content=query)
    ]
    used_tools = []
    llm = get_llm(llm_mode)
    
    try:
        for _ in range(3): # Max cycles
            res = llm.invoke(messages)
            content = res.content.strip() if hasattr(res, "content") else str(res).strip()
            
            # Coba cari blok JSON di dalam konten respon (bisa lebih dari satu)
            json_blocks = extract_json_objects(content)
            if json_blocks:
                has_executed_any = False
                for block in json_blocks:
                    try:
                        data = json.loads(block)
                        action = data.get("action")
                        action_input = data.get("action_input", {})
                        
                        if action in TOOL_DISPATCHER:
                            used_tools.append(action)
                            has_executed_any = True
                            try:
                                observation = TOOL_DISPATCHER[action](**action_input)
                                messages.append(HumanMessage(content=f"Data RAG / API berhasil ditarik untuk tool {action}:\n{observation}"))
                            except Exception as e:
                                messages.append(HumanMessage(content=f"Gagal menjalankan tool {action} karena error: {str(e)}."))
                    except json.JSONDecodeError:
                        pass
                
                if has_executed_any:
                    messages.append(HumanMessage(content="Semua data di atas telah berhasil ditarik. Sekarang, berikan jawaban akhir Bahasa Indonesia yang ramah, komprehensif, dan tepat kepada pengguna berdasarkan data tersebut."))
                    continue
                    
            # Jika AI mengeluarkan teks bahasa natural (bukan JSON tulen) atau tool tidak ada
            # Anggap ini sebagai final answer dan keluar dari loop mempercepat respons!
            return content, used_tools
    except Exception as e:
        error_str = str(e)
        if "GITHUB_TOKEN_MISSING" in error_str:
            return "Maaf, sistem dikonfigurasi menggunakan GitHub Models API, namun GITHUB_TOKEN belum diatur. Masukkan Token Anda ke file .env.", []
        elif "401" in error_str or "Unauthorized" in error_str:
            return "Maaf, GITHUB_TOKEN Anda tidak valid atau tidak memiliki akses ke model. Silakan periksa kembali kredensial Anda di file .env.", []
        elif "429" in error_str or "rate limit" in error_str.lower():
            return "Maaf, batas penggunaan (rate limit) API GitHub Models telah tercapai. Silakan coba lagi nanti.", []
        else:
            return f"Terjadi kesalahan internal API: {error_str}", []

    return content, used_tools

# Compatibility wrapper
def ambil_profil_petani():
    PROFILE_FILE = "storage/farmer_profile.json"
    if not os.path.exists(PROFILE_FILE): return None
    try:
        with open(PROFILE_FILE, "r") as f:
            return json.loads(encryptor.decrypt(f.read()))
    except Exception as e:
        print(f"[Get Profile Error] {e}")
        return None

llm_final = RunnableLambda(lambda x: ask_chatbot(x.to_string() if hasattr(x, "to_string") else str(x), "local")[0])

if __name__ == "__main__":
    print(ask_chatbot("Berapa harga cabai di Malang?"))