"""
knowledge_agent.py — Knowledge Agent
===================================
Specialized agent for agricultural guidance using RAG.
"""

from typing import Any, Dict, Optional, List
from datetime import datetime
from .base_agent import ReactAgent
from .memory import AgentMemory
from .tools_enhanced import get_tool


class KnowledgeAgent(ReactAgent):
    """
    Knowledge Agent - Provides expert agricultural guidance.
    
    Responsibilities:
    - Pest and disease identification
    - Crop care guidance
    - Best practices recommendations
    - Troubleshooting agricultural problems
    - Educational content delivery
    """
    
    def __init__(self, memory: Optional[AgentMemory] = None):
        super().__init__(
            agent_id="knowledge_agent",
            name="Knowledge Agent",
            description="Provides agricultural expertise and guidance",
            memory=memory or AgentMemory("knowledge_agent")
        )
        self.rag_tool = get_tool("tanya_panduan")
        self.expertise_areas = [
            "pest_management",
            "disease_control",
            "crop_care",
            "soil_management",
            "irrigation",
            "fertilization",
            "harvesting"
        ]
        
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Return available tools."""
        return [
            {
                "name": "tanya_panduan",
                "description": "Query agricultural guidance from documents",
                "params": ["query"]
            }
        ]
    
    def plan(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Plan knowledge query handling."""
        # Identify expertise area
        expertise = self._identify_expertise_area(query)
        
        plan = {
            "reasoning": f"Knowledge query about {expertise}, retrieving from RAG",
            "needs_action": True,
            "tool": "tanya_panduan",
            "tool_params": {"query": query},
            "expertise_area": expertise
        }
        
        return plan
    
    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Execute a knowledge tool."""
        if tool_name == "tanya_panduan":
            result = self.rag_tool.execute(**params)
            if result.get("success"):
                # Store in memory for future reference
                self.memory.remember(f"query_{datetime.now().timestamp()}", result, persistent=True)
            return result
        return {"error": f"Unknown tool: {tool_name}"}
    
    def reason(self, observations: Dict[str, Any]) -> str:
        """Generate expert guidance based on retrieved knowledge."""
        if "last_observation" not in observations:
            return "Tidak dapat mengambil panduan. Silakan coba lagi."
        
        knowledge_data = observations["last_observation"]
        
        if not knowledge_data.get("success"):
            return f"Gagal mengambil panduan: {knowledge_data.get('error', 'Unknown error')}"
        
        context = knowledge_data.get("context", "")
        
        response = "📚 Panduan Pertanian:\n"
        response += "=" * 50 + "\n"
        response += context + "\n"
        response += "=" * 50 + "\n\n"
        
        # Add expert commentary
        expertise = observations.get("expertise_area", "general")
        commentary = self._add_expert_commentary(expertise, context)
        
        if commentary:
            response += "💡 Catatan Ahli:\n"
            response += commentary + "\n\n"
        
        # Add actionable tips
        tips = self._generate_actionable_tips(expertise)
        if tips:
            response += "✅ Langkah Praktis:\n"
            for tip in tips:
                response += f"• {tip}\n"
        
        return response
    
    def _identify_expertise_area(self, query: str) -> str:
        """Identify which expertise area the query relates to."""
        query_lower = query.lower()
        
        area_keywords = {
            "pest_management": ["hama", "pest", "serangga", "infestasi"],
            "disease_control": ["penyakit", "busuk", "layu", "bercak"],
            "crop_care": ["perawatan", "pemeliharaan", "tumbuh", "berkembang"],
            "soil_management": ["tanah", "kesuburan", "pupuk", "ph"],
            "irrigation": ["air", "siram", "irigasi", "kelembaban"],
            "fertilization": ["pupuk", "nitrogen", "fosfor", "kalium"],
            "harvesting": ["panen", "saat panen", "umur panen", "hasil"]
        }
        
        for area, keywords in area_keywords.items():
            if any(kw in query_lower for kw in keywords):
                return area
        
        return "general"
    
    def _add_expert_commentary(self, expertise: str, context: str) -> str:
        """Add expert commentary based on expertise area."""
        commentaries = {
            "pest_management": "Pengendalian hama organik lebih aman dan berkelanjutan dibanding kimia.",
            "disease_control": "Pencegahan lebih efektif dari pengobatan - jaga kebersihan dan drainase.",
            "crop_care": "Monitoring tanaman secara rutin membantu deteksi dini masalah.",
            "soil_management": "Pengujian tanah sebelum tanam penting untuk menentukan kebutuhan nutrisi.",
            "irrigation": "Irigasi yang tepat waktu mencegah stress air pada tanaman.",
            "fertilization": "Pupuk sesuai kebutuhan tanaman menghindari pemborosan dan pencemaran.",
            "harvesting": "Waktu panen yang optimal menghasilkan kualitas dan kuantitas terbaik."
        }
        
        return commentaries.get(expertise, "")
    
    def _generate_actionable_tips(self, expertise: str) -> List[str]:
        """Generate practical tips based on expertise area."""
        tips_map = {
            "pest_management": [
                "Monitor tanaman 2-3 kali per minggu untuk deteksi awal hama",
                "Gunakan perangkap warna atau feromon untuk monitoring",
                "Isolasi tanaman yang terinfeksi untuk mencegah penyebaran"
            ],
            "disease_control": [
                "Pastikan drainage baik untuk mencegah kelembaban berlebih",
                "Buang bagian tanaman yang terinfeksi penyakit",
                "Gunakan benih varietas yang resisten penyakit"
            ],
            "crop_care": [
                "Berikan naungan jika diperlukan saat cuaca ekstrem",
                "Lakukan pemangkasan untuk stimulasi pertumbuhan lateral",
                "Jaga kebersihan area sekitar tanaman dari gulma"
            ],
            "soil_management": [
                "Lakukan rotasi tanaman untuk menjaga kesuburan tanah",
                "Tambahkan kompos atau bahan organik secara berkala",
                "Hindari pemadatan tanah dengan lalu lintas berlebihan"
            ],
            "irrigation": [
                "Siram di pagi atau sore hari untuk efisiensi maksimal",
                "Ukur kelembaban tanah sebelum menyiram",
                "Gunakan mulsa untuk menjaga kelembaban tanah"
            ],
            "fertilization": [
                "Aplikasikan pupuk sesuai dengan fase pertumbuhan tanaman",
                "Gunakan pupuk organik sebagai suplemen pupuk anorganik",
                "Hindari pemupukan berlebihan yang dapat menyebabkan kelayuan"
            ],
            "harvesting": [
                "Panen pagi hari saat kelembaban tinggi untuk kesegaran",
                "Gunakan alat yang bersih dan tajam untuk mencegah kerusakan",
                "Tangani hasil panen dengan hati-hati untuk kualitas terbaik"
            ]
        }
        
        return tips_map.get(expertise, [
            "Ikuti panduan yang diberikan dengan seksama",
            "Catat setiap aktivitas untuk pembelajaran berkelanjutan",
            "Konsultasikan dengan ahli lokal jika ada kendala"
        ])
    
    def get_expert_answer(self, question: str) -> str:
        """Get expert answer for a specific question."""
        return self.react_loop(question, {})
    
    def search_by_topic(self, topic: str) -> Dict[str, Any]:
        """Search knowledge base by topic."""
        result = self.rag_tool.execute(query=topic)
        
        if result.get("success"):
            return {
                "topic": topic,
                "knowledge": result.get("context", ""),
                "documents_found": result.get("document_count", 0),
                "timestamp": datetime.now().isoformat()
            }
        
        return {"error": "Topic not found in knowledge base"}
    
    def process_query(self, query: str, context: Dict[str, Any] = None) -> str:
        """Main entry point for processing knowledge queries."""
        context = context or {}
        return self.react_loop(query, context)
