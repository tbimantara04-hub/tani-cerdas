"""
AGENTIC SYSTEM GUIDE
===================
Comprehensive guide to Tani-Cerdas Multi-Agent Agentic System.
"""

# ============================================================
# OVERVIEW
# ============================================================
"""
Tani-Cerdas has been transformed into a sophisticated multi-agent
agentic system. Instead of a single ReAct loop, the system now uses
5 specialized agents coordinated by a central orchestrator.
"""

# ============================================================
# ARCHITECTURE
# ============================================================
"""
┌─────────────────────────────────────────────────┐
│ FRONTEND (React + Vite)                          │
│ - Chatbot widget updated for multi-agent         │
│ - Agent selection/delegation UI                  │
│ - Workflow execution interface                   │
└────────────────────┬────────────────────────────┘
                     │
            HTTP/REST API (FastAPI)
            /api/chat
            /api/workflow
            /api/status
            /api/agents
                     │
                     ↓
    ┌────────────────────────────────────┐
    │ AGENT ORCHESTRATOR                 │
    │ - Routes queries to agents          │
    │ - Manages inter-agent comm          │
    │ - Aggregates responses              │
    │ - Maintains farmer context          │
    └───────┬─────────────────────────────┘
            │
    ┌───────┴───────────────────────────────┐
    │                                       │
    ↓           ↓            ↓             ↓             ↓
┌────────┐ ┌────────┐ ┌────────┐ ┌──────────┐ ┌─────────┐
│Weather │ │ Price  │ │  Farm  │ │ Knowledge│ │Advisory │
│ Agent  │ │ Agent  │ │ Agent  │ │  Agent   │ │ Agent   │
└───┬────┘ └───┬────┘ └───┬────┘ └────┬─────┘ └────┬────┘
    │          │          │           │            │
    └──────────┴──────────┴───────────┴────────────┘
                │
    ┌───────────────────────────┐
    │ Agent Memory System        │
    │ - Short-term memory        │
    │ - Long-term memory         │
    │ - Pattern learning         │
    │ - Farmer context tracking  │
    └───────────────────────────┘
"""

# ============================================================
# AGENT DESCRIPTIONS
# ============================================================

"""
1. WEATHER AGENT
   - Real-time weather monitoring
   - Weather alerts and warnings
   - Seasonal pattern recognition
   - Crop-specific weather recommendations
   
   Keywords that trigger this agent:
   cuaca, weather, hujan, panas, dingin, angin, iklim

2. PRICE AGENT
   - Commodity price monitoring
   - Fertilizer price tracking
   - Price trend analysis
   - Optimal selling/buying time prediction
   - Budget planning assistance
   
   Keywords that trigger this agent:
   harga, price, jual, beli, pasar, pupuk, benih

3. FARM AGENT
   - Crop planting schedules
   - Field management
   - Input tracking (seeds, fertilizer, water)
   - Harvest planning
   - Multi-field coordination
   
   Keywords that trigger this agent:
   tanam, panen, lahan, jadwal, rencana, catat, aktivitas

4. KNOWLEDGE AGENT
   - Pest identification and management
   - Disease control guidance
   - Crop care best practices
   - Troubleshooting problems
   - Educational content delivery
   
   Keywords that trigger this agent:
   hama, penyakit, pestisida, obat, panduan, cara, teknik

5. ADVISORY AGENT
   - Farmer pattern analysis
   - Personalized recommendations
   - Risk identification
   - Optimization suggestions
   - Long-term planning advice
   
   Keywords that trigger this agent:
   saran, rekomendasi, analisis, insight, strategi
"""

# ============================================================
# USAGE EXAMPLES
# ============================================================

"""
EXAMPLE 1: Simple Chat Query
────────────────────────────
User: "Bagaimana cuaca hari ini di Bogor?"
Flow:
  1. Orchestrator receives query
  2. Identifies "weather" as relevant agent (keyword: "cuaca")
  3. Routes to WeatherAgent
  4. WeatherAgent calls cek_cuaca tool
  5. Returns weather data with crop recommendations

Response:
  📍 Cuaca di Bogor:
  🌡️ Suhu: 28°C (terasa 29°C)
  💨 Angin: 5 km/h
  💧 Kelembaban: 72%
  🌦️ Kondisi: Berawan
  🌾 Rekomendasi: Cuaca mendukung - lanjutkan aktivitas di lapangan


EXAMPLE 2: Multi-Agent Workflow
────────────────────────────────
User: "Tolong rencana tanam padi saya tahun ini"
Flow:
  1. Orchestrator receives query
  2. Identifies "farm" as primary agent (keyword: "tanam")
  3. FarmAgent creates planting plan using PlanningAgent pattern
  4. Orchestrator also routes to AdvisoryAgent for recommendations
  5. Aggregates responses

Response:
  📋 Rencana Pertanian Anda:
  ✓ Tanaman: Padi
    Durasi: 120 hari
    Musim: Wet Season
    Kebutuhan Air: High
  
  Jadwal:
    - 2026-06-23: Persiapan lahan dan penanaman
    - 2026-07-23: Pemupukan pertama
    - 2026-08-22: Pemupukan kedua dan monitoring hama
    - 2026-10-21: Panen
  
  🎯 Analisis & Rekomendasi:
  💡 Rekomendasi:
    • Siapkan 120kg benih berkualitas
    • Pastikan drainase lahan sudah baik
    • Siapkan 50kg Urea dan 50kg NPK


EXAMPLE 3: Programmatic Workflow Execution
──────────────────────────────────────────
POST /api/workflow
{
  "farmer_id": "farmer123",
  "steps": [
    {
      "agent": "farm",
      "action": "create_plan",
      "params": {"crop": "padi", "area_size": 1.5}
    },
    {
      "agent": "knowledge",
      "action": "search_by_topic",
      "params": {"topic": "pemupukan padi"}
    },
    {
      "agent": "price",
      "action": "get_price_forecast",
      "params": {"commodity": "beras", "days_ahead": 30}
    }
  ]
}

Response:
{
  "workflow_status": "complete",
  "total_steps": 3,
  "results": [
    {
      "step": 0,
      "agent": "farm",
      "action": "create_plan",
      "success": true,
      "result": {...planting plan...}
    },
    {
      "step": 1,
      "agent": "knowledge",
      "action": "search_by_topic",
      "success": true,
      "result": {...guidance...}
    },
    {
      "step": 2,
      "agent": "price",
      "action": "get_price_forecast",
      "success": true,
      "result": {...forecast...}
    }
  ]
}
"""

# ============================================================
# API ENDPOINTS (UPDATED)
# ============================================================

"""
NEW/UPDATED ENDPOINTS:

1. POST /api/chat
   Purpose: Send message to agentic system
   Body: {
     "message": "string",
     "farmer_id": "string (optional, default='default')"
   }
   Response: {
     "response": "string",
     "agent": "string (primary agent used)",
     "farmer_id": "string"
   }

2. POST /api/workflow (NEW)
   Purpose: Execute multi-agent workflow
   Body: {
     "farmer_id": "string",
     "steps": [
       {
         "agent": "string",
         "action": "string",
         "params": {object}
       }
     ]
   }
   Response: {
     "workflow_status": "string",
     "results": [...],
     "timestamp": "string"
   }

3. GET /api/status (NEW)
   Purpose: Get system status
   Response: {
     "system": "operational",
     "agents": {agent status summaries},
     "timestamp": "string"
   }

4. GET /api/agents (NEW)
   Purpose: List available agents and their capabilities
   Response: {
     "agents": ["weather", "price", "farm", "knowledge", "advisory"],
     "total_agents": 5,
     "active_agents": number,
     "timestamp": "string"
   }

5. GET /api/agents/{agent_id} (NEW)
   Purpose: Get detailed info about specific agent
   Parameters: agent_id (string)
   Response: {
     "agent": {summary},
     "available_tools": [...],
     "memory_summary": {...}
   }

UNCHANGED ENDPOINTS:
- GET /api/history
- GET /api/profile
- POST /api/profile
- POST /api/planting
- GET /api/planting
"""

# ============================================================
# MIGRATION GUIDE
# ============================================================

"""
STEP 1: Backup Current System
  - Keep old main.py as main_legacy.py
  - Export chat history and profiles

STEP 2: Install New Files
  - Copy agents/ directory to backend/
  - Update requirements.txt if needed
  - Add main_agentic.py to backend/

STEP 3: Update Environment
  - Ensure .env has ENCRYPTION_KEY
  - Ensure Ollama is running with required models:
    * qwen2:1.5b
    * nomic-embed-text

STEP 4: Start New System
  - Option A (Direct switch):
    python main_agentic.py
  
  - Option B (Run both):
    # Keep legacy on port 8000
    python main.py
    # Run agentic on port 8001
    python -m uvicorn main_agentic:app --port 8001

STEP 5: Update Frontend
  - Update API endpoint from localhost:8000 to localhost:8001 (if running both)
  - Chatbot component already works with new API
  - Can add agent selection UI (optional)

STEP 6: Testing
  - Test basic chat functionality
  - Test workflows
  - Monitor agent logs
  - Verify farmer profiles load correctly
"""

# ============================================================
# AGENT MEMORY SYSTEM
# ============================================================

"""
Each agent maintains two types of memory:

SHORT-TERM MEMORY (Working Memory)
  - Stores current task context
  - Limited to 10 items
  - Cleared after task completion
  - Fast access

LONG-TERM MEMORY (Persistent)
  - Observations: Historical data points
  - Patterns: Learned patterns from data
  - Learnings: Insights and discoveries
  - Context History: Farmer-specific contexts
  - Storage: JSON files in storage/agent_memory/

FARMER CONTEXT
  - Profile: Crop type, land size, location
  - Recent Queries: Last 50 queries
  - Active Concerns: Identified problems
  - Achievements: Successful outcomes
  - Storage: storage/farmer_{farmer_id}_context.json

Memory helps agents:
  ✓ Learn from past interactions
  ✓ Identify patterns and trends
  ✓ Provide personalized recommendations
  ✓ Detect anomalies
  ✓ Improve recommendations over time
"""

# ============================================================
# CUSTOMIZATION & EXTENSION
# ============================================================

"""
CREATING A NEW AGENT:

1. Create file: backend/agents/custom_agent.py
   
2. Implement:
   ```python
   from .base_agent import ReactAgent
   from .memory import AgentMemory
   
   class CustomAgent(ReactAgent):
       def __init__(self, memory=None):
           super().__init__(
               agent_id="custom_agent",
               name="Custom Agent",
               description="Your agent description"
           )
           
       def get_available_tools(self):
           return [...]
       
       def plan(self, query, context):
           return {...}
       
       def execute_tool(self, tool_name, params):
           return {...}
       
       def reason(self, observations):
           return \"...\"
       
       def process_query(self, query, context=None):
           context = context or {}
           return self.react_loop(query, context)
   ```

3. Register in orchestrator.py:
   ```python
   from .custom_agent import CustomAgent
   
   # In __init__:
   self.agents["custom"] = CustomAgent(AgentMemory("custom_agent", self.storage))
   ```

4. Update keyword mapping in _determine_relevant_agents():
   ```python
   "custom": ["your", "keywords", "here"]
   ```
"""

# ============================================================
# PERFORMANCE & OPTIMIZATION
# ============================================================

"""
AGENT OPTIMIZATION:

1. Caching
   - WeatherTool caches results for 1 hour
   - FAISS vector store cached locally
   - Farmer profiles cached in memory

2. Limiting Iterations
   - max_iterations = 3 per agent
   - Prevents infinite loops
   - Fast response times

3. Parallel Processing
   - Orchestrator can route to multiple agents
   - Responses aggregated and synthesized
   - User sees comprehensive answer quickly

4. Memory Management
   - Short-term memory bounded to 10 items
   - Long-term memory keeps last 100 observations
   - Old data automatically pruned

MONITORING:
   - GET /api/status shows agent states
   - Background monitoring runs every 1 hour
   - Alerts generated for anomalies
   - All interactions logged to encrypted storage
"""

# ============================================================
# TROUBLESHOOTING
# ============================================================

"""
ISSUE: "Agent not found" error
SOLUTION:
  - Check agent_id is registered in orchestrator.__init__()
  - Verify agent class is imported
  - Check /api/status to see available agents

ISSUE: Ollama models not found
SOLUTION:
  - ollama pull qwen2:1.5b
  - ollama pull nomic-embed-text
  - Check Ollama is running: ollama serve

ISSUE: Memory files not being saved
SOLUTION:
  - Check storage/ directory exists
  - Verify write permissions
  - Check ENCRYPTION_KEY in .env

ISSUE: Slow responses
SOLUTION:
  - Check number of iterations (reduce max_iterations)
  - Clear memory cache periodically
  - Monitor FAISS index size
  - Check system resources

ISSUE: Queries not routed to correct agent
SOLUTION:
  - Add keywords to _determine_relevant_agents()
  - Check keyword mapping matches domain
  - Review orchestrator logs
"""

# ============================================================
# DEPLOYMENT
# ============================================================

"""
PRODUCTION DEPLOYMENT:

1. Configure CORS properly (not * in production)
2. Use environment variables for sensitive data
3. Set up monitoring and logging
4. Use process manager (pm2, systemd, etc.)
5. Enable HTTPS/SSL
6. Set up database for user management
7. Implement rate limiting
8. Enable authentication tokens
9. Set up backup strategy
10. Monitor agent performance metrics

Example systemd service:
  [Unit]
  Description=Tani-Cerdas Agentic API
  After=network.target

  [Service]
  Type=simple
  User=www-data
  WorkingDirectory=/path/to/backend
  ExecStart=/usr/bin/python3 main_agentic.py
  Restart=always

  [Install]
  WantedBy=multi-user.target
"""

print("=" * 60)
print("TANI-CERDAS AGENTIC SYSTEM - SETUP GUIDE")
print("=" * 60)
print("For full documentation, see this file.")
print("API running at: http://localhost:8000")
print("=" * 60)
