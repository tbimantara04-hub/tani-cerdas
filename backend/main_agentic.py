"""
main_agentic.py — Updated FastAPI Backend with Agentic System
============================================================
Integrates the multi-agent orchestrator with the REST API.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.orchestrator import AgentOrchestrator
from security import encryptor
from guardrails import validate_agricultural_query
import uvicorn
import json
import os
from datetime import datetime
import threading
import time


app = FastAPI(
    title="Tani-Cerdas AI Assistant API (Agentic)",
    description="Multi-agent agricultural assistance system"
)

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

# Initialize orchestrator (singleton)
orchestrator = None

def get_orchestrator():
    global orchestrator
    if orchestrator is None:
        print("Initializing AgentOrchestrator...")
        orchestrator = AgentOrchestrator()
    return orchestrator

# File paths for simple storage
PLANTING_FILE = "storage/planting_records.json"
CHAT_HISTORY_FILE = "storage/chat_history.json"
FARMER_PROFILE_FILE = "storage/farmer_profile.json"

# Background monitoring thread
monitoring_thread = None
monitoring_active = False

def save_encrypted_data(file_path, data):
    """Save encrypted data to file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    json_data = json.dumps(data)
    encrypted_data = encryptor.encrypt(json_data)
    with open(file_path, "w") as f:
        f.write(encrypted_data)

def load_decrypted_data(file_path):
    """Load and decrypt data from file."""
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r") as f:
        encrypted_data = f.read()
    
    if not encrypted_data:
        return []
        
    try:
        decrypted_json = encryptor.decrypt(encrypted_data)
    except Exception as e:
        print(f"[Storage] Decryption failed: {e}")
        return []

    try:
        return json.loads(decrypted_json)
    except json.JSONDecodeError as e:
        print(f"[Storage] JSON decode error: {e}")
        return []

def load_farmer_profile(farmer_id: str = "default"):
    """Load farmer profile from encrypted storage."""
    data = load_decrypted_data(FARMER_PROFILE_FILE)
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and item.get("farmer_id") == farmer_id:
                return item
    elif isinstance(data, dict):
        return data
    return None

def save_farmer_profile(farmer_id: str, profile: dict):
    """Save farmer profile to encrypted storage."""
    os.makedirs(os.path.dirname(FARMER_PROFILE_FILE), exist_ok=True)
    profiles = load_decrypted_data(FARMER_PROFILE_FILE)
    
    if not isinstance(profiles, list):
        profiles = []
    
    # Update or add farmer profile
    found = False
    for i, p in enumerate(profiles):
        if isinstance(p, dict) and p.get("farmer_id") == farmer_id:
            profiles[i] = {**p, **profile, "farmer_id": farmer_id}
            found = True
            break
    
    if not found:
        profiles.append({**profile, "farmer_id": farmer_id})
    
    save_encrypted_data(FARMER_PROFILE_FILE, profiles)

def background_monitoring():
    """Monitor farmers in background."""
    global monitoring_active
    print("[Background] Starting farmer monitoring...")
    
    while monitoring_active:
        try:
            orch = get_orchestrator()
            alerts = orch.monitor_all_farmers()
            
            if alerts:
                print(f"[Background] Generated {len(alerts)} alerts")
                for alert in alerts:
                    print(f"  - Alert for {alert.payload.get('farmer_id')}: {alert.content}")
            
            time.sleep(3600)  # Check every hour
        except Exception as e:
            print(f"[Background] Error in monitoring: {e}")

def start_background_monitoring():
    """Start background monitoring thread."""
    global monitoring_thread, monitoring_active
    if not monitoring_active:
        monitoring_active = True
        monitoring_thread = threading.Thread(target=background_monitoring, daemon=True)
        monitoring_thread.start()
        print("Background monitoring started")

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    farmer_id: str = "default"
    llm_mode: str = "local"

class ChatResponse(BaseModel):
    response: str
    agent: str = "orchestrator"
    farmer_id: str

class FarmerProfile(BaseModel):
    tanaman: str
    luas_lahan: str
    lokasi: str = ""
    farmer_id: str = "default"

class WorkflowStep(BaseModel):
    agent: str
    action: str
    params: dict = {}

class WorkflowRequest(BaseModel):
    steps: list[WorkflowStep]
    farmer_id: str = "default"

# Routes
@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    get_orchestrator()
    start_background_monitoring()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global monitoring_active
    monitoring_active = False

@app.get("/")
async def root():
    """API info."""
    orch = get_orchestrator()
    summary = orch.get_orchestrator_summary()
    return {
        "message": "Welcome to Tani-Cerdas Agentic AI Assistant API",
        "version": "2.0-agentic",
        "orchestrator": summary
    }

@app.get("/api/status")
async def get_status():
    """Get system status."""
    orch = get_orchestrator()
    return {
        "system": "operational",
        "agents": orch.get_agent_status(),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Chat endpoint - processes queries through the agentic system.
    """
    try:
        if not request.message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Get orchestrator
        orch = get_orchestrator()
        
        # Load farmer profile for context
        profile = load_farmer_profile(request.farmer_id)
        if profile:
            orch.set_farmer_profile(request.farmer_id, profile)
        
        # Guardrail check
        is_allowed, warning_msg = validate_agricultural_query(request.message, request.llm_mode)
        if not is_allowed:
            bot_response = warning_msg
            primary_agent = "guardrail"
            result = {"response": bot_response, "primary_agent": primary_agent, "status": "blocked"}
        else:
            # Process query through orchestrator
            # Add llm_mode to kwargs to pass down to agents if needed in future
            result = orch.process_query(request.message, request.farmer_id, llm_mode=request.llm_mode)
            bot_response = result.get("response", "No response")
            primary_agent = result.get("primary_agent", "unknown")
        
        # Save to chat history
        history = load_decrypted_data(CHAT_HISTORY_FILE)
        history.append({
            "farmer_id": request.farmer_id,
            "timestamp": datetime.now().isoformat(),
            "user": request.message,
            "bot": bot_response,
            "agent": primary_agent,
            "full_result": result
        })
        save_encrypted_data(CHAT_HISTORY_FILE, history)
        
        return ChatResponse(
            response=bot_response,
            agent=primary_agent,
            farmer_id=request.farmer_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
def get_history(farmer_id: str = "default"):
    """Get chat history for a farmer."""
    history = load_decrypted_data(CHAT_HISTORY_FILE)
    
    if farmer_id != "all":
        history = [h for h in history if h.get("farmer_id") == farmer_id]
    
    return history

@app.get("/api/profile")
def get_profile(farmer_id: str = "default"):
    """Get farmer profile."""
    profile = load_farmer_profile(farmer_id)
    if not profile:
        return {"farmer_id": farmer_id, "tanaman": "", "luas_lahan": "", "lokasi": ""}
    return profile

@app.post("/api/profile")
def update_profile(request: FarmerProfile):
    """Update farmer profile."""
    try:
        profile_data = {
            "tanaman": request.tanaman,
            "luas_lahan": request.luas_lahan,
            "lokasi": request.lokasi,
            "farmer_id": request.farmer_id,
            "updated_at": datetime.now().isoformat()
        }
        
        save_farmer_profile(request.farmer_id, profile_data)
        
        # Update in orchestrator
        orch = get_orchestrator()
        orch.set_farmer_profile(request.farmer_id, profile_data)
        
        return {
            "status": "success",
            "message": "Profil berhasil diperbarui",
            "profile": profile_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents")
def get_agents():
    """Get information about available agents."""
    orch = get_orchestrator()
    summary = orch.get_orchestrator_summary()
    return summary

@app.post("/api/workflow")
def execute_workflow(request: WorkflowRequest):
    """
    Execute a multi-agent workflow.
    
    Example:
    {
        "farmer_id": "farmer1",
        "steps": [
            {"agent": "farm", "action": "create_plan", "params": {"crop": "padi", "area_size": 1.0}},
            {"agent": "weather", "action": "check", "params": {"lokasi": "Bogor"}},
            {"agent": "knowledge", "action": "search_by_topic", "params": {"topic": "padi"}}
        ]
    }
    """
    try:
        orch = get_orchestrator()
        
        # Convert workflow steps to proper format
        steps = []
        for step in request.steps:
            steps.append({
                "agent": step.agent,
                "action": step.action,
                "params": step.params
            })
        
        # Execute workflow
        result = orch.execute_multi_agent_workflow(steps, request.farmer_id)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/planting")
def save_planting(record: dict, farmer_id: str = "default"):
    """Save planting record."""
    try:
        records = load_decrypted_data(PLANTING_FILE)
        new_record = {
            **record,
            "farmer_id": farmer_id,
            "date": record.get("date") or datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().isoformat()
        }
        
        records.append(new_record)
        save_encrypted_data(PLANTING_FILE, records)
        
        return {
            "status": "success",
            "message": "Catatan penanaman berhasil disimpan",
            "record": new_record
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/planting")
def get_planting(farmer_id: str = "default"):
    """Get planting records."""
    records = load_decrypted_data(PLANTING_FILE)
    
    if farmer_id != "all":
        records = [r for r in records if r.get("farmer_id") == farmer_id]
    
    return records

@app.get("/api/agents/{agent_id}")
def get_agent_details(agent_id: str):
    """Get details about a specific agent."""
    orch = get_orchestrator()
    agent = orch.agents.get(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    return {
        "agent": agent.get_summary(),
        "available_tools": agent.get_available_tools(),
        "memory_summary": agent.memory.get_summary() if hasattr(agent, "memory") else {}
    }

if __name__ == "__main__":
    uvicorn.run("main_agentic:app", host="0.0.0.0", port=8000, reload=True)
