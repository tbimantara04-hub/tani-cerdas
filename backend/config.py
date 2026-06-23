"""
config.py — System Configuration
==============================
Configuration for Tani-Cerdas system selection and behavior.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# SYSTEM MODE
# ============================================================

# Options: "agentic" (new multi-agent) or "legacy" (old single-agent)
SYSTEM_MODE = os.getenv("SYSTEM_MODE", "agentic")

# ============================================================
# API CONFIGURATION
# ============================================================

if SYSTEM_MODE == "agentic":
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
    CHAT_ENDPOINT = "/api/chat"
    HISTORY_ENDPOINT = "/api/history"
    PROFILE_ENDPOINT = "/api/profile"
    PLANTING_ENDPOINT = "/api/planting"
    STATUS_ENDPOINT = "/api/status"
    WORKFLOW_ENDPOINT = "/api/workflow"
    AGENTS_ENDPOINT = "/api/agents"
else:
    # Legacy system
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
    CHAT_ENDPOINT = "/api/chat"
    HISTORY_ENDPOINT = "/api/history"
    PROFILE_ENDPOINT = "/api/profile"
    PLANTING_ENDPOINT = "/api/planting"

# ============================================================
# AGENTIC SYSTEM CONFIGURATION
# ============================================================

if SYSTEM_MODE == "agentic":
    AGENT_CONFIG = {
        "weather": {
            "enabled": True,
            "keywords": ["cuaca", "weather", "hujan", "panas", "angin"],
            "timeout": 10
        },
        "price": {
            "enabled": True,
            "keywords": ["harga", "price", "pasar", "jual", "beli"],
            "timeout": 5
        },
        "farm": {
            "enabled": True,
            "keywords": ["tanam", "panen", "lahan", "jadwal", "rencana"],
            "timeout": 10
        },
        "knowledge": {
            "enabled": True,
            "keywords": ["hama", "penyakit", "panduan", "cara", "tips"],
            "timeout": 15
        },
        "advisory": {
            "enabled": True,
            "keywords": ["saran", "rekomendasi", "analisis", "insight"],
            "timeout": 10
        }
    }
    
    # Agent behavior
    MAX_AGENT_ITERATIONS = int(os.getenv("MAX_AGENT_ITERATIONS", "3"))
    ENABLE_BACKGROUND_MONITORING = os.getenv("ENABLE_BACKGROUND_MONITORING", "true").lower() == "true"
    MONITORING_INTERVAL_HOURS = int(os.getenv("MONITORING_INTERVAL_HOURS", "1"))
    
    # Agent memory
    MEMORY_STORAGE_DIR = os.getenv("MEMORY_STORAGE_DIR", "storage/agent_memory")
    ENABLE_PERSISTENT_MEMORY = os.getenv("ENABLE_PERSISTENT_MEMORY", "true").lower() == "true"

# ============================================================
# ENCRYPTION
# ============================================================

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "your-secret-key-here")

# ============================================================
# DATABASE / STORAGE
# ============================================================

STORAGE_DIR = os.getenv("STORAGE_DIR", "storage")
VECTORSTORE_DIR = os.getenv("VECTORSTORE_DIR", "storage/vectorstore/db_faiss_local")
DATA_DIR = os.getenv("DATA_DIR", "data")

# ============================================================
# OLLAMA CONFIGURATION
# ============================================================

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL_CHAT = os.getenv("OLLAMA_MODEL_CHAT", "qwen2:1.5b")
OLLAMA_MODEL_EMBED = os.getenv("OLLAMA_MODEL_EMBED", "nomic-embed-text")

OLLAMA_CONFIG = {
    "temperature": 0.1,
    "num_gpu": 0,  # Set to > 0 if GPU available
    "num_predict": 1024,
}

# ============================================================
# EXTERNAL APIS
# ============================================================

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

# ============================================================
# LOGGING
# ============================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ENABLE_AGENT_LOGGING = os.getenv("ENABLE_AGENT_LOGGING", "true").lower() == "true"

# ============================================================
# FRONTEND CONFIGURATION
# ============================================================

FRONTEND_CONFIG = {
    "system_mode": SYSTEM_MODE,
    "api_base_url": API_BASE_URL,
    "enable_agent_selection": SYSTEM_MODE == "agentic",
    "enable_workflow_builder": SYSTEM_MODE == "agentic",
    "show_agent_status": SYSTEM_MODE == "agentic",
    "theme": "light"  # Options: "light", "dark"
}

# ============================================================
# FEATURE FLAGS
# ============================================================

FEATURES = {
    "enable_chat": True,
    "enable_voice": True,
    "enable_profile": True,
    "enable_planting_records": True,
    "enable_workflows": SYSTEM_MODE == "agentic",
    "enable_agent_dashboard": SYSTEM_MODE == "agentic",
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_api_url(endpoint):
    """Get full API URL for an endpoint."""
    return f"{API_BASE_URL}{endpoint}"

def is_agentic_mode():
    """Check if system is in agentic mode."""
    return SYSTEM_MODE == "agentic"

def is_agent_enabled(agent_id):
    """Check if a specific agent is enabled."""
    if not is_agentic_mode():
        return False
    return AGENT_CONFIG.get(agent_id, {}).get("enabled", False)

def get_agent_keywords(agent_id):
    """Get keywords that trigger an agent."""
    if not is_agentic_mode():
        return []
    return AGENT_CONFIG.get(agent_id, {}).get("keywords", [])

# ============================================================
# VALIDATION
# ============================================================

def validate_config():
    """Validate configuration settings."""
    errors = []
    
    # Check encryption key
    if ENCRYPTION_KEY == "your-secret-key-here":
        errors.append("WARNING: Using default ENCRYPTION_KEY. Set ENCRYPTION_KEY env var for production.")
    
    # Check agentic-specific config
    if is_agentic_mode():
        # These will be checked when agents initialize
        pass
    
    return errors

# Print validation warnings on import
if __name__ != "__main__":
    validation_errors = validate_config()
    if validation_errors:
        import warnings
        for error in validation_errors:
            warnings.warn(error, UserWarning)

# ============================================================
# ENVIRONMENT INFO
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TANI-CERDAS SYSTEM CONFIGURATION")
    print("=" * 60)
    print(f"System Mode: {SYSTEM_MODE}")
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Storage Directory: {STORAGE_DIR}")
    print(f"Ollama Model (Chat): {OLLAMA_MODEL_CHAT}")
    print(f"Ollama Model (Embed): {OLLAMA_MODEL_EMBED}")
    print()
    
    if is_agentic_mode():
        print("Agentic System Configuration:")
        print(f"  Max Agent Iterations: {MAX_AGENT_ITERATIONS}")
        print(f"  Background Monitoring: {ENABLE_BACKGROUND_MONITORING}")
        print(f"  Monitoring Interval: {MONITORING_INTERVAL_HOURS} hours")
        print(f"  Persistent Memory: {ENABLE_PERSISTENT_MEMORY}")
        print()
        print("Enabled Agents:")
        for agent_id, config in AGENT_CONFIG.items():
            if config.get("enabled"):
                print(f"  ✓ {agent_id.upper()}")
    else:
        print("Running in LEGACY mode")
    
    print()
    print("Features Enabled:")
    for feature, enabled in FEATURES.items():
        status = "✓" if enabled else "✗"
        print(f"  {status} {feature}")
    
    print()
    print("Configuration Validation:")
    errors = validate_config()
    if errors:
        for error in errors:
            print(f"  ⚠️ {error}")
    else:
        print("  ✓ All configurations valid")
    
    print("=" * 60)
