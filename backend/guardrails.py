import os
import re
from typing import Tuple
from langchain_core.messages import SystemMessage, HumanMessage

# Daftar kata kunci pertanian & tanaman (Indonesian & English)
AGRI_KEYWORDS = [
    "tani", "tanam", "pertanian", "petani", "kebun", "sawah", "padi", "jagung", 
    "cabai", "cabe", "bawang", "pupuk", "hama", "penyakit", "panen", "cuaca", 
    "hujan", "tanah", "irigasi", "lahan", "benih", "bibit", "urea", "npk", 
    "pestisida", "herbisida", "sayur", "buah", "komoditas", "pasar", "harga", 
    "beras", "singkong", "ubi", "hortikultura", "organik", "gulma", "ulat", 
    "wereng", "belalang", "drainase", "mulsa", "cangkul", "traktor", "tanaman",
    "peternakan", "ternak", "perikanan", "kolam", "hewan", "pakan", "siram", 
    "cuaca", "iklim", "suhu", "kelembaban", "angin", "hujan", "kemarau", "agro"
]

# Sapaan & obrolan asisten umum (dibuat spesifik untuk menghindari kecocokan kata tanya umum)
CONV_KEYWORDS = [
    "halo", "hai", "selamat pagi", "selamat siang", "selamat sore", "selamat malam", 
    "assalamualaikum", "apa kabar", "terima kasih", "makasih", "siapa kamu",
    "nama kamu", "fiturmu", "panduan", "cara pakai", "asisten tani"
]

def is_query_allowed_by_keywords(query: str) -> bool:
    query_lower = query.lower()
    # Cocokan kata kunci
    for kw in AGRI_KEYWORDS + CONV_KEYWORDS:
        if kw in query_lower:
            return True
    return False

def validate_agricultural_query(query: str, llm_mode: str = "local") -> Tuple[bool, str]:
    """
    Memvalidasi apakah input pengguna berkaitan dengan pertanian atau tani.
    Mengembalikan (is_allowed, response_message)
    """
    if not query:
        return False, "Pesan tidak boleh kosong."
        
    query_lower = query.lower()
    
    # 1. Deteksi Prompt Injection dasar
    injection_patterns = [
        r"ignore (all )?(previous|prior|above) instructions",
        r"disregard (your )?(system|previous)",
        r"reveal (your )?(system prompt|api key|token|secret)",
        r"act as (dan|jailbreak|unrestricted)",
        r"system prompt",
        r"tuliskan kode",
        r"buatkan program",
        r"__import__",
        r"os\.system"
    ]
    for pattern in injection_patterns:
        if re.search(pattern, query_lower, re.IGNORECASE):
            return False, "Maaf, pesan Anda mengandung instruksi keamanan yang tidak diizinkan."

    # 2. Cek kecocokan kata kunci (Fast path)
    if is_query_allowed_by_keywords(query):
        return True, ""

    # 3. Klasifikasi menggunakan LLM jika ambigu / tidak ada kata kunci
    try:
        from rag_logic import get_llm
        llm = get_llm(llm_mode)
        
        prompt = (
            "Tugasmu menentukan apakah pertanyaan pengguna berkaitan dengan pertanian, perkebunan, peternakan, perikanan, cuaca, harga pangan, atau sapaan asisten pertanian.\n\n"
            "Aturan Penilaian:\n"
            "- Jawab HANYA dengan kata 'YA' jika berkaitan dengan topik pertanian/cuaca/harga pangan/sapaan asisten.\n"
            "- Jawab HANYA dengan kata 'TIDAK' jika tidak berkaitan (misal: meminta coding, sejarah umum, politik, matematika, dll).\n\n"
            f"Pertanyaan pengguna: \"{query}\"\n\n"
            "Jawaban (YA/TIDAK):"
        )
        
        messages = [
            SystemMessage(content="Kamu adalah filter asisten pertanian Tani-Cerdas."),
            HumanMessage(content=prompt)
        ]
        
        res = llm.invoke(messages)
        content = res.content.strip().upper() if hasattr(res, "content") else str(res).strip().upper()
        
        if "YA" in content:
            return True, ""
        else:
            return False, "Maaf, saya hanya dapat menjawab pertanyaan seputar pertanian dan tani."
            
    except Exception as e:
        print(f"[Guardrails] Error during LLM check: {e}")
        # Jika LLM gagal, dan tidak lolos kata kunci, tolak demi keamanan
        return False, "Maaf, saya hanya dapat menjawab pertanyaan seputar pertanian dan tani."
