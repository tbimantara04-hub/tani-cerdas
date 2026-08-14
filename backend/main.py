from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_logic import ask_chatbot, ambil_profil_petani, simpan_profil_petani
from security import encryptor
from guardrails import validate_agricultural_query
import uvicorn
import json
import os
from datetime import datetime

app = FastAPI(title="Tani-Cerdas AI Assistant API")

# Configure CORS
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000")
allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# File paths for simple storage
PLANTING_FILE = "storage/planting_records.json"
CHAT_HISTORY_FILE = "storage/chat_history.json"

def save_encrypted_data(file_path, data):
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    # Enkripsi data sebelum disimpan (Data at Rest)
    json_data = json.dumps(data)
    encrypted_data = encryptor.encrypt(json_data)
    with open(file_path, "w") as f:
        f.write(encrypted_data)

def load_decrypted_data(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r") as f:
        encrypted_data = f.read()
    
    if not encrypted_data:
        return []
        
    decrypted_json = encryptor.decrypt(encrypted_data)
    try:
        return json.loads(decrypted_json)
    except json.JSONDecodeError as e:
        print(f"[Storage] JSON decode error: {e}")
        return []

class ChatRequest(BaseModel):
    message: str
    llm_mode: str = "local"

class ChatResponse(BaseModel):
    response: str

@app.get("/")
async def root():
    return {"message": "Welcome to Tani-Cerdas AI Assistant API"}

# Perbaikan: Menggunakan 'def' biasa (bukan 'async def') 
# agar fungsi background dari LangChain tidak memblokir server
@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        if not request.message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Guardrail check
        is_allowed, warning_msg = validate_agricultural_query(request.message, request.llm_mode)
        if not is_allowed:
            bot_response = warning_msg
        else:
            bot_result = ask_chatbot(request.message, request.llm_mode)
            bot_response = bot_result[0] if isinstance(bot_result, tuple) else bot_result
        
        # Simpan riwayat chat secara terenkripsi
        history = load_decrypted_data(CHAT_HISTORY_FILE)
        history.append({
            "timestamp": datetime.now().isoformat(),
            "user": request.message,
            "bot": bot_response
        })
        save_encrypted_data(CHAT_HISTORY_FILE, history)
        
        return ChatResponse(response=bot_response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
def get_history():
    # Mengambil riwayat yang sudah didekripsi oleh backend
    return load_decrypted_data(CHAT_HISTORY_FILE)

class PlantingRecord(BaseModel):
    plant_name: str
    notes: str
    date: str = None

@app.post("/api/planting")
def save_planting(record: PlantingRecord):
    try:
        records = load_decrypted_data(PLANTING_FILE)
        new_record = record.model_dump()
        if not new_record["date"]:
            new_record["date"] = datetime.now().strftime("%Y-%m-%d")
        
        records.append(new_record)
        save_encrypted_data(PLANTING_FILE, records)
        return {"status": "success", "message": "Catatan penanaman berhasil disimpan secara aman."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/planting")
def get_planting():
    return load_decrypted_data(PLANTING_FILE)

class FarmerProfileRequest(BaseModel):
    tanaman: str
    luas_lahan: str

@app.get("/api/profile")
def get_profile():
    profile = ambil_profil_petani()
    if not profile:
        return {"tanaman": "", "luas_lahan": ""}
    return profile

@app.post("/api/profile")
def update_profile(request: FarmerProfileRequest):
    result = simpan_profil_petani(tanaman=request.tanaman, luas_lahan=request.luas_lahan)
    if "Gagal" in result:
        raise HTTPException(status_code=500, detail=result)
    return {"status": "success", "message": result}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)