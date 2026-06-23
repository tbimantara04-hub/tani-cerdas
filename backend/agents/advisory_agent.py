"""
advisory_agent.py — Advisory Agent
==================================
Specialized agent for proactive recommendations and insights.
"""

from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta
from .base_agent import Agent, AgentState, AgentMessage
from .memory import AgentMemory, FarmerContext


class AdvisoryAgent(Agent):
    """
    Advisory Agent - Provides proactive recommendations and insights.
    
    Responsibilities:
    - Analyze farmer patterns and history
    - Provide personalized recommendations
    - Alert on anomalies or risks
    - Suggest optimization opportunities
    - Long-term planning advice
    """
    
    def __init__(self, memory: Optional[AgentMemory] = None):
        super().__init__(
            agent_id="advisory_agent",
            name="Advisory Agent",
            description="Provides proactive recommendations and insights",
            memory=memory or AgentMemory("advisory_agent")
        )
        self.recommendation_threshold = 0.7  # Confidence threshold
        
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Return available tools."""
        return [
            {
                "name": "analyze_patterns",
                "description": "Analyze farmer's historical patterns",
                "params": ["farmer_id"]
            },
            {
                "name": "generate_insights",
                "description": "Generate insights from data",
                "params": ["farmer_id"]
            }
        ]
    
    def plan(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Plan advisory query handling."""
        farmer_id = context.get("farmer_id", "default")
        
        plan = {
            "reasoning": f"Analyzing patterns and generating recommendations for farmer {farmer_id}",
            "needs_action": True,
            "farmer_id": farmer_id,
            "analysis_depth": "comprehensive"
        }
        
        return plan
    
    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Execute an advisory tool."""
        if tool_name == "analyze_patterns":
            return self._analyze_patterns(params.get("farmer_id", "default"))
        elif tool_name == "generate_insights":
            return self._generate_insights(params.get("farmer_id", "default"))
        return {"error": f"Unknown tool: {tool_name}"}
    
    def _analyze_patterns(self, farmer_id: str) -> Dict[str, Any]:
        """Analyze farmer's historical patterns."""
        # Get farmer context
        farmer_context = FarmerContext(farmer_id, self.memory.storage if hasattr(self.memory, 'storage') else None)
        profile = farmer_context.get_profile()
        
        analysis = {
            "farmer_id": farmer_id,
            "profile": profile,
            "patterns": {},
            "anomalies": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Analyze query patterns
        recent_queries = farmer_context.context.get("recent_queries", [])
        if recent_queries:
            query_topics = {}
            for q in recent_queries[-20:]:  # Last 20 queries
                topic = self._categorize_query(q.get("query", ""))
                query_topics[topic] = query_topics.get(topic, 0) + 1
            analysis["patterns"]["query_interests"] = query_topics
        
        # Analyze concerns
        recent_concerns = farmer_context.get_recent_concerns(days=90)
        if recent_concerns:
            concern_types = {}
            for c in recent_concerns:
                concern = c.get("concern", {})
                ctype = concern.get("type", "unknown")
                concern_types[ctype] = concern_types.get(ctype, 0) + 1
            analysis["patterns"]["concern_distribution"] = concern_types
        
        return analysis
    
    def _generate_insights(self, farmer_id: str) -> Dict[str, Any]:
        """Generate insights from farmer data."""
        farmer_context = FarmerContext(farmer_id, self.memory.storage if hasattr(self.memory, 'storage') else None)
        
        insights = {
            "farmer_id": farmer_id,
            "insights": [],
            "recommendations": [],
            "risks": [],
            "opportunities": []
        }
        
        profile = farmer_context.get_profile()
        crop = profile.get("tanaman", "").lower()
        
        # Generate insights based on pattern
        if crop:
            insights["insights"].append(f"Farmer fokus pada tanaman {crop}")
            
            # Seasonal recommendations
            current_month = datetime.now().month
            if crop == "padi" and current_month in [10, 11, 12]:
                insights["recommendations"].append("Musim tanam padi dimulai - siapkan benih berkualitas")
            
            # Risk assessment
            recent_concerns = farmer_context.get_recent_concerns(days=30)
            if len(recent_concerns) > 3:
                insights["risks"].append("Frekuensi masalah meningkat - perlu monitoring intensif")
        
        # Opportunities
        recent_queries = farmer_context.context.get("recent_queries", [])
        if len(recent_queries) < 5:
            insights["opportunities"].append("Kurangnya interaksi - manfaatkan konsultasi AI lebih sering")
        
        return insights
    
    def _categorize_query(self, query: str) -> str:
        """Categorize a query topic."""
        query_lower = query.lower()
        
        if any(w in query_lower for w in ["hama", "pest", "serangga"]):
            return "pest_management"
        elif any(w in query_lower for w in ["penyakit", "disease"]):
            return "disease"
        elif any(w in query_lower for w in ["harga", "price", "jual"]):
            return "market"
        elif any(w in query_lower for w in ["cuaca", "weather", "hujan"]):
            return "weather"
        elif any(w in query_lower for w in ["pupuk", "fertilizer"]):
            return "fertilization"
        elif any(w in query_lower for w in ["tanam", "plant", "panen"]):
            return "planting"
        else:
            return "general"
    
    def reason(self, observations: Dict[str, Any]) -> str:
        """Generate comprehensive advisory response."""
        patterns = observations.get("patterns", {})
        insights = observations.get("insights", {})
        
        response = "🎯 Analisis & Rekomendasi:\n"
        response += "=" * 50 + "\n\n"
        
        # Pattern summary
        if insights.get("insights"):
            response += "📊 Temuan:\n"
            for insight in insights.get("insights", []):
                response += f"• {insight}\n"
            response += "\n"
        
        # Recommendations
        if insights.get("recommendations"):
            response += "💡 Rekomendasi:\n"
            for rec in insights.get("recommendations", []):
                response += f"• {rec}\n"
            response += "\n"
        
        # Risk alerts
        if insights.get("risks"):
            response += "⚠️ Perhatian:\n"
            for risk in insights.get("risks", []):
                response += f"• {risk}\n"
            response += "\n"
        
        # Opportunities
        if insights.get("opportunities"):
            response += "🌟 Peluang:\n"
            for opp in insights.get("opportunities", []):
                response += f"• {opp}\n"
        
        return response
    
    def generate_personalized_advice(self, farmer_id: str, topic: str) -> str:
        """Generate personalized advice for a farmer."""
        farmer_context = FarmerContext(farmer_id, self.memory.storage if hasattr(self.memory, 'storage') else None)
        profile = farmer_context.get_profile()
        
        advice = f"💼 Saran Personal untuk {farmer_id}:\n"
        advice += f"Tanaman: {profile.get('tanaman', 'Unknown')}\n"
        advice += f"Luas: {profile.get('luas_lahan', 'Unknown')}\n\n"
        
        # Generate topic-specific advice
        if "market" in topic.lower():
            advice += "Strategi Pasar:\n"
            advice += "• Pantau harga min 2x per minggu untuk timing panen optimal\n"
            advice += "• Hubungkan dengan koperasi untuk akses pasar yang lebih luas\n"
            advice += "• Diversifikasi produk untuk mengurangi risiko\n"
        elif "production" in topic.lower():
            advice += "Strategi Produksi:\n"
            advice += "• Terapkan rotasi tanaman untuk menjaga kesuburan tanah\n"
            advice += "• Gunakan bibit unggul berkualitas tinggi\n"
            advice += "• Monitor hasil panen setiap musim untuk evaluasi\n"
        elif "risk" in topic.lower():
            advice += "Manajemen Risiko:\n"
            advice += "• Siapkan asuransi pertanian untuk perlindungan\n"
            advice += "• Diversifikasi jenis tanaman untuk mengurangi risiko\n"
            advice += "• Pelajari teknik adaptif terhadap perubahan iklim\n"
        
        return advice
    
    def monitor_farmer(self, farmer_id: str) -> Optional[AgentMessage]:
        """Monitor farmer and generate alert if needed."""
        farmer_context = FarmerContext(farmer_id, self.memory.storage if hasattr(self.memory, 'storage') else None)
        
        # Check for anomalies
        recent_concerns = farmer_context.get_recent_concerns(days=7)
        
        if len(recent_concerns) > 2:
            # Multiple concerns in short period - alert
            message = AgentMessage(
                sender=self.agent_id,
                recipient="broadcast",
                intent="alert",
                content=f"Farmer {farmer_id} memiliki beberapa masalah baru",
                payload={
                    "farmer_id": farmer_id,
                    "concern_count": len(recent_concerns),
                    "concerns": recent_concerns
                }
            )
            return message
        
        return None
    
    def process_query(self, query: str, context: Dict[str, Any] = None) -> str:
        """Main entry point for processing advisory queries."""
        context = context or {}
        farmer_id = context.get("farmer_id", "default")
        
        # Analyze patterns
        patterns = self._analyze_patterns(farmer_id)
        
        # Generate insights
        insights = self._generate_insights(farmer_id)
        
        # Build observations for reasoning
        observations = {
            "patterns": patterns,
            "insights": insights,
            "farmer_id": farmer_id
        }
        
        # Reason and generate response
        response = self.reason(observations)
        return response
