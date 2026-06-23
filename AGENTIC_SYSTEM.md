# Tani-Cerdas Agentic System v2.0

## 🎯 Overview

Tani-Cerdas has been completely transformed into a **sophisticated multi-agent system**. Instead of a single AI model handling all queries, the system now uses **5 specialized agents** working together to provide comprehensive agricultural assistance.

## ✨ Key Improvements

✅ **Specialized Expertise** - Each agent focuses on specific domain (weather, prices, farm management, knowledge, advisory)  
✅ **Better Context Awareness** - Agents maintain farmer-specific memory and context  
✅ **Proactive Insights** - Advisory agent provides recommendations based on patterns  
✅ **Multi-Step Workflows** - Complex tasks broken into coordinated steps  
✅ **Improved Accuracy** - Focused agents make better decisions in their domain  
✅ **Persistent Learning** - Agents learn from farmer history  

## 🤖 The Five Agents

### 1. **Weather Agent** 🌦️
Monitors and provides weather information, alerts, and crop-specific recommendations.

**Triggers:** "Berapa cuaca hari ini?", "Akan hujan?", "Ada peringatan cuaca?"

**Capabilities:**
- Real-time weather data from OpenWeatherMap API
- Weather alerts and critical condition warnings
- Seasonal pattern recognition
- Crop-specific recommendations based on weather
- 1-hour weather data caching for efficiency

**Response Example:**
```
📍 Cuaca di Bogor:
🌡️ Suhu: 28°C (terasa 29°C)
💨 Angin: 5 km/h
💧 Kelembaban: 72%
🌦️ Kondisi: Berawan

⚠️ PERINGATAN: Kelembaban sangat tinggi - risiko penyakit jamur meningkat

🌾 Rekomendasi:
• Pastikan drainase berfungsi baik
• Monitor untuk tanda-tanda penyakit jamur
• Tingkatkan ventilasi di greenhouse
```

---

### 2. **Price Agent** 💰
Tracks commodity and fertilizer prices, analyzes trends, and recommends optimal trading times.

**Triggers:** "Berapa harga beras?", "Kapan waktu jual padi?", "Harga pupuk sekarang"

**Capabilities:**
- Real-time commodity price lookup
- Fertilizer price tracking
- Price trend analysis over 7+ days
- Optimal selling time recommendations
- Budget planning for inputs
- Historical price comparison

**Response Example:**
```
💰 Harga Pangan:
─────────────────────────────────────────────
Beras............................. Rp 13,500/kg
Cabai Rawit....................... Rp 48,000/kg
Bawang Merah...................... Rp 32,000/kg
Jagung............................ Rp 5,500/kg
─────────────────────────────────────────────

📊 Analisis Tren:
• Harga beras stabil minggu ini
• Cabai menunjukkan tren naik 5%
• Waktu terbaik jual: bulan depan saat supply berkurang

💡 Rekomendasi Pasar:
• Manfaatkan harga tinggi cabai sekarang jika memiliki stok
• Catat harga harian untuk pattern recognition
• Koordinasi dengan petani lain untuk negosiasi lebih kuat
```

---

### 3. **Farm Agent** 🌾
Plans planting schedules, manages field records, and coordinates multi-field operations.

**Triggers:** "Rencana tanam padi", "Kapan panen?", "Catat aktivitas tanam"

**Capabilities:**
- Crop planting schedules with milestones
- Input requirements calculation (seeds, fertilizer)
- Yield estimation based on crop and area
- Field activity logging
- Multi-crop planning and rotation
- Harvest timeline planning

**Response Example:**
```
📋 Rencana Pertanian Anda:
==================================================

✓ Tanaman: Padi
  Durasi: 120 hari
  Musim: Musim Hujan
  Kebutuhan Air: Tinggi

  Jadwal:
    - 2026-06-23: Persiapan lahan dan penanaman
    - 2026-07-23: Pemupukan pertama
    - 2026-08-22: Pemupukan kedua dan monitoring hama
    - 2026-10-21: PANEN

  Input yang Dibutuhkan:
    - Benih: ~20kg
    - Urea: ~50kg
    - NPK: ~50kg
    - Air: 1000mm untuk musim tanam

  Estimasi Hasil:
    - Perkiraan: ~500kg gabah kering
    - Kepercayaan: Medium
    - Faktor: Cuaca, kesuburan tanah, manajemen hama

==================================================

💡 Tips:
• Catat setiap aktivitas pertanian untuk monitoring
• Ikuti jadwal pemupukan dan penyiraman
• Siapkan tindakan antisipasi hama sebelumnya
```

---

### 4. **Knowledge Agent** 📚
Provides expert agricultural guidance using RAG (Retrieval-Augmented Generation) from documents.

**Triggers:** "Bagaimana cara mengatasi hama?", "Penyakit apa ini?", "Tips bertanam padi"

**Capabilities:**
- RAG-based knowledge retrieval from agricultural documents
- Pest and disease identification
- Best practices recommendations
- Troubleshooting agricultural problems
- Step-by-step guidance for complex tasks
- Educational content delivery with expert commentary

**Response Example:**
```
📚 Panduan Pertanian:
==================================================

[Retrieved from agricultural document]

Untuk mengatasi hama Wereng pada padi:
1. Monitoring: Periksa 2-3x per minggu dengan sweeping net
2. Pengendalian Kultur: Buang gulma yang menjadi inang
3. Varietas Tahan: Gunakan varietas yang tahan wereng
4. Karantina: Isolasi tanaman terinfeksi
5. Kontrol Biologis: Gunakan musuh alami (laba-laba, wasp)
6. Pestisida: Jika perlu, gunakan insektisida nabati

==================================================

💡 Catatan Ahli:
Pengendalian hama organik lebih aman dan berkelanjutan dibanding kimia.

✅ Langkah Praktis:
• Monitor tanaman 2-3 kali per minggu untuk deteksi awal hama
• Gunakan perangkap warna atau feromon untuk monitoring
• Isolasi tanaman yang terinfeksi untuk mencegah penyebaran
• Catat semua aktivitas pengendalian hama
```

---

### 5. **Advisory Agent** 🎯
Analyzes farmer patterns and provides personalized, proactive recommendations.

**Triggers:** "Berikan saran", "Analisis pola", "Apa risiko?", "Peluang apa?"

**Capabilities:**
- Historical pattern analysis
- Personalized recommendations based on farmer profile
- Risk identification and assessment
- Opportunity discovery
- Seasonal planning advice
- Long-term optimization suggestions
- Anomaly detection and alerts

**Response Example:**
```
🎯 Analisis & Rekomendasi Personal:
==================================================

📊 Temuan:
• Farmer fokus pada tanaman Padi
• Musim tanam padi dimulai bulan depan
• Frekuensi masalah meningkat dalam 30 hari terakhir

💡 Rekomendasi:
• Siapkan benih berkualitas tinggi
• Perkuat sistem drainase lahan
• Tingkatkan monitoring hama minggu ke-3 hingga ke-5

⚠️ Perhatian:
• Frekuensi masalah meningkat - perlu monitoring intensif
• Pastikan pasokan pupuk tersedia sebelum musim tanam
• Persiapkan strategi pengendalian hama

🌟 Peluang:
• Harga beras meningkat - pertahankan kualitas
• Diversifikasi dengan tanaman pendamping
• Bergabung dengan kelompok tani untuk kekuatan negosiasi
```

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────┐
│ FRONTEND (React/Vue)                         │
│ - Chatbot Widget                             │
│ - Workflow Builder                           │
│ - Dashboard with Agent Status                │
└────────────┬────────────────────────────────┘
             │
    HTTP/REST API (FastAPI)
    - /api/chat          (Send query)
    - /api/workflow      (Execute workflow)
    - /api/status        (System status)
    - /api/agents        (List agents)
             │
             ↓
┌────────────────────────────────────────────┐
│ ORCHESTRATOR                                │
│ - Routes queries to agents                  │
│ - Manages inter-agent communication         │
│ - Aggregates responses                      │
│ - Maintains farmer context                  │
└───────┬──────────────┬──────────────────────┘
        │              │
   ┌────┴──┬───┬──┬──┬─┴────┐
   │       │   │  │  │      │
   ↓       ↓   ↓  ↓  ↓      ↓
┌──────┐┌──────┐┌──────┐┌──────────┐┌───────┐
│Weathr││Price ││ Farm ││Knowledge ││Adviso │
│Agent ││Agent ││Agent ││  Agent   ││ Agent │
└──────┘└──────┘└──────┘└──────────┘└───────┘
   │       │      │        │           │
   └───────┴──────┴────────┴───────────┘
           │
       ┌───┴────────────────────┐
       │ AGENT MEMORY SYSTEM     │
       │ - Short-term memory     │
       │ - Long-term memory      │
       │ - Pattern learning      │
       │ - Farmer context        │
       └────────────────────────┘
```

---

## 🚀 Getting Started

### Installation

1. **Ensure backend requirements are installed:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Make sure Ollama models are available:**
   ```bash
   ollama pull qwen2:1.5b
   ollama pull nomic-embed-text
   ```

3. **Ensure Ollama is running:**
   ```bash
   ollama serve  # In another terminal
   ```

### Starting the System

**Option 1: Full Agentic System (Recommended)**
```bash
cd backend
python main_agentic.py
# API runs at http://localhost:8000
```

**Option 2: Run alongside legacy system**
```bash
# Terminal 1 - Legacy system
cd backend
python main.py  # Runs on port 8000

# Terminal 2 - New agentic system
cd backend
uvicorn main_agentic:app --port 8001 --reload
```

### Testing the API

1. **Simple Chat Query:**
   ```bash
   curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Bagaimana cuaca hari ini?",
       "farmer_id": "farmer1"
     }'
   ```

2. **Get System Status:**
   ```bash
   curl http://localhost:8000/api/status
   ```

3. **Execute Workflow:**
   ```bash
   curl -X POST http://localhost:8000/api/workflow \
     -H "Content-Type: application/json" \
     -d '{
       "farmer_id": "farmer1",
       "steps": [
         {
           "agent": "farm",
           "action": "create_plan",
           "params": {"crop": "padi", "area_size": 1.0}
         },
         {
           "agent": "knowledge",
           "action": "search_by_topic",
           "params": {"topic": "pemupukan padi"}
         }
       ]
     }'
   ```

---

## 📊 API Endpoints

### Chat Endpoint
```
POST /api/chat

Body:
{
  "message": "string (the query)",
  "farmer_id": "string (optional, default='default')"
}

Response:
{
  "response": "string (agent response)",
  "agent": "string (which agent handled it)",
  "farmer_id": "string"
}
```

### Workflow Execution
```
POST /api/workflow

Body:
{
  "farmer_id": "string",
  "steps": [
    {
      "agent": "string (weather|price|farm|knowledge|advisory)",
      "action": "string (process_query|create_plan|etc)",
      "params": {object with action-specific parameters}
    }
  ]
}

Response:
{
  "workflow_status": "string",
  "total_steps": number,
  "results": [{step results}],
  "timestamp": "ISO string"
}
```

### Status & Agent Info
```
GET /api/status
GET /api/agents
GET /api/agents/{agent_id}
```

---

## 💾 Agent Memory System

Each agent maintains **two types of memory:**

### Short-Term Memory (Working Memory)
- Current task context
- Limited to 10 items
- Fast access
- Cleared after task completion

### Long-Term Memory (Persistent)
- **Observations:** Historical data points
- **Patterns:** Learned patterns from behavior
- **Learnings:** Insights and discoveries
- **Context History:** Farmer-specific contexts

**Storage Location:** `storage/agent_memory/`

**Farmer Context:** `storage/farmer_{farmer_id}_context.json`

This allows agents to:
- Learn from past interactions
- Identify trends and patterns
- Provide personalized recommendations
- Detect anomalies
- Improve continuously over time

---

## 🔄 Agent Collaboration Example

**Scenario:** Farmer asks "Rencana tanam padi saya bulan depan apa saja?"

1. **Orchestrator** analyzes query → identifies "farm" as primary agent
2. **FarmAgent** creates planting plan with:
   - Planting schedule with milestones
   - Input requirements (seeds, fertilizer, water)
   - Yield estimation
3. **Orchestrator** also routes to **AdvisoryAgent**
4. **AdvisoryAgent** analyzes farmer's history and adds:
   - Personalized risk warnings
   - Opportunities based on farmer profile
   - Recommendations from past successful harvests
5. **Orchestrator** aggregates both responses
6. **Farmer** receives comprehensive, personalized plan

---

## 🛠️ Extending the System

### Creating a New Agent

1. Create `backend/agents/custom_agent.py`:
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
        return "..."
    
    def process_query(self, query, context=None):
        context = context or {}
        return self.react_loop(query, context)
```

2. Register in `orchestrator.py`:
```python
self.agents["custom"] = CustomAgent(AgentMemory("custom_agent"))
```

3. Add keywords to `_determine_relevant_agents()`

---

## 📈 Performance Optimizations

- **Caching:** Weather data cached for 1 hour
- **Memory Bounds:** Short-term memory limited to 10 items
- **Iteration Limit:** Max 3 iterations per agent to ensure fast responses
- **Parallel Processing:** Multiple agents can process simultaneously
- **Auto-Pruning:** Old observations automatically removed

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Agent not found | Check agent registered in orchestrator |
| Ollama models missing | `ollama pull qwen2:1.5b` |
| Memory not saving | Check storage/ directory permissions |
| Slow responses | Reduce max_iterations or check system load |
| Wrong agent routing | Review keywords in `_determine_relevant_agents()` |

---

## 📝 License & Attribution

Based on original Tani-Cerdas platform. Enhanced with multi-agent architecture.

---

## 🤝 Contributing

To contribute:
1. Create a new agent following the Agent interface
2. Register it in the orchestrator
3. Add integration tests
4. Update documentation

---

## 📞 Support

For issues or questions:
1. Check AGENTIC_GUIDE.py for detailed documentation
2. Review agent logs in terminal
3. Check storage/agent_memory/ for agent state
4. Test endpoints using provided curl examples

---

**Version:** 2.0-Agentic  
**Last Updated:** 2026-06-23  
**Status:** Production Ready ✅
