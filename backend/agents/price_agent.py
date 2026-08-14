"""
price_agent.py — Price Agent
============================
Specialized agent for market monitoring, price analysis, and recommendations.
"""

from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from .base_agent import ReactAgent, AgentMessage
from .memory import AgentMemory
from .tools_enhanced import get_tool


class PriceAgent(ReactAgent):
    """
    Price Agent - Handles commodity and fertilizer price monitoring.
    
    Responsibilities:
    - Real-time price checks
    - Price trend analysis
    - Market recommendations
    - Optimal selling/buying time prediction
    - Budget planning for farmers
    """
    
    def __init__(self, memory: Optional[AgentMemory] = None):
        super().__init__(
            agent_id="price_agent",
            name="Price Agent",
            description="Monitors market prices and provides trading recommendations",
            memory=memory or AgentMemory("price_agent")
        )
        self.price_tool = get_tool("cek_harga")
        
    def get_available_tools(self) -> list[Dict[str, Any]]:
        """Return available tools."""
        return [
            {
                "name": "cek_harga",
                "description": "Check commodity or fertilizer prices",
                "params": ["jenis", "komoditas"]
            }
        ]
    
    def plan(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Plan price query handling."""
        jenis = "pangan" if any(x in query.lower() for x in ["harga", "padi", "jagung", "cabai", "beras"]) else "pupuk"
        
        # Extract commodity if mentioned
        komoditas = ""
        commodities = ["beras", "cabai", "bawang", "jagung", "urea", "npk", "pupuk"]
        for item in commodities:
            if item in query.lower():
                komoditas = item
                break
        
        plan = {
            "reasoning": f"Checking {jenis} prices, commodity: {komoditas}",
            "needs_action": True,
            "tool": "cek_harga",
            "tool_params": {
                "jenis": jenis,
                "komoditas": komoditas
            },
            "analyze_trends": "trend" in query.lower()
        }
        
        return plan
    
    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Execute a price tool."""
        if tool_name == "cek_harga":
            result = self.price_tool.execute(**params)
            if result.get("success"):
                self._record_price_data(result)
            return result
        return {"error": f"Unknown tool: {tool_name}"}
    
    def _record_price_data(self, price_data: Dict[str, Any]):
        """Record price data for trend analysis."""
        jenis = price_data.get("jenis", "unknown")
        key = f"prices_{jenis}_{datetime.now().strftime('%Y%m%d')}"
        self.memory.remember(key, price_data, persistent=True)
    
    def reason(self, observations: Dict[str, Any]) -> str:
        """Reason about prices and provide market recommendations."""
        if "last_observation" not in observations:
            return "Tidak dapat mengambil data harga. Silakan coba lagi."
        
        price_data = observations["last_observation"]
        
        if not price_data.get("success"):
            return f"Gagal mengecek harga: {price_data.get('error', 'Unknown error')}"
        
        jenis = price_data.get("jenis", "").title()
        items = price_data.get("items", {})
        
        response = f"💰 Harga {jenis}:\n"
        response += "─" * 40 + "\n"
        
        for item, price in items.items():
            response += f"{item.title():.<30} Rp {int(price):>8,}/kg\n"
        
        response += "─" * 40 + "\n\n"
        
        # Analyze trends
        trends = self._analyze_trends(jenis.lower(), items)
        if trends:
            response += "📊 Analisis Tren:\n"
            for trend in trends:
                response += f"• {trend}\n"
            response += "\n"
        
        # Provide recommendations
        recommendations = self._get_market_recommendations(jenis.lower(), items)
        if recommendations:
            response += "💡 Rekomendasi Pasar:\n"
            for rec in recommendations:
                response += f"• {rec}\n"
        
        return response
    
    def _analyze_trends(self, jenis: str, items: Dict[str, str]) -> list[str]:
        """
        Analyze price trends using historical price records from the persistent memory.
        Calculates percentage changes and gives actionable trend warnings.
        """
        trends = []
        
        # Get historical data
        today = datetime.now()
        found_historical = False
        
        # Compare with yesterday or recent days (up to 7 days ago)
        for i in range(1, 8):
            prev_date = (today - timedelta(days=i)).strftime("%Y%m%d")
            prev_key = f"prices_{jenis}_{prev_date}"
            prev_prices = self.memory.recall(prev_key)
            
            if prev_prices and isinstance(prev_prices, dict) and prev_prices.get("success"):
                prev_items = prev_prices.get("items", {})
                found_historical = True
                trends.append(f"Perbandingan tren harga dengan {i} hari lalu ({prev_date}):")
                
                for item, current_val in items.items():
                    if item in prev_items:
                        try:
                            curr_price = float(current_val)
                            prev_price = float(prev_items[item])
                            if prev_price > 0:
                                pct_change = ((curr_price - prev_price) / prev_price) * 100
                                if pct_change > 0:
                                    trends.append(f"• {item.title()}: naik +{pct_change:.1f}%")
                                elif pct_change < 0:
                                    trends.append(f"• {item.title()}: turun {pct_change:.1f}%")
                                else:
                                    trends.append(f"• {item.title()}: stabil (tidak ada perubahan)")
                        except (ValueError, TypeError):
                            pass
                break
                
        if not found_historical:
            trends.append("Belum ada data historis di memori untuk perbandingan tren jangka pendek.")
            
        # Generic trend analysis
        if jenis == "pangan":
            trends.append("Amati fluktuasi mingguan untuk menentukan waktu penjualan yang paling optimal.")
        else:
            trends.append("Harga pupuk subsidi diatur HET pemerintah sehingga cenderung stabil.")
        
        return trends
    
    def _get_market_recommendations(self, jenis: str, items: Dict[str, str]) -> list[str]:
        """Get market recommendations based on prices."""
        recommendations = []
        
        if jenis == "pangan":
            # Pangan recommendations
            recommendations.append("Monitor harga untuk menentukan waktu panen terbaik")
            recommendations.append("Pertimbangkan untuk menjual saat harga mencapai puncak musiman")
            recommendations.append("Manfaatkan kurir pengumpul untuk mengurangi biaya distribusi")
        else:
            # Pupuk recommendations
            recommendations.append("Pupuk subsidi lebih ekonomis - prioritaskan penggunaan jenis ini")
            recommendations.append("Beli pupuk sebelum musim tanam untuk menghindari kelangkaan")
            recommendations.append("Pastikan penyimpanan pupuk pada tempat yang kering dan tertutup")
        
        return recommendations
    
    def get_price_forecast(self, commodity: str, days_ahead: int = 30) -> Dict[str, Any]:
        """
        Predict price movements for a commodity based on simulated weekly seasonal cycles.
        This uses a rule-based seasonal forecasting heuristic to simulate supply/demand fluctuations.
        """
        forecast = {
            "commodity": commodity,
            "forecast_days": days_ahead,
            "predictions": [],
            "confidence": 0.6,
            "timestamp": datetime.now().isoformat(),
            "model_type": "seasonal_heuristic_v1"
        }
        
        for day in range(1, days_ahead + 1):
            date = (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d")
            # Heuristic seasonal simulation: weekly cycle variation
            variation = day % 7
            change_percentage = variation - 3
            forecast["predictions"].append({
                "date": date,
                "trend": "increasing" if change_percentage > 0 else ("decreasing" if change_percentage < 0 else "stable"),
                "expected_change": f"{change_percentage}%" if change_percentage != 0 else "0%"
            })
        
        return forecast
    
    def suggest_selling_time(self, crop: str) -> Dict[str, Any]:
        """Suggest optimal time to sell a crop."""
        return {
            "crop": crop,
            "recommendation": "Monitor harga dan jual saat mencapai puncak pasar",
            "factors": [
                "Musim panen puncak (lebih banyak supply = harga rendah)",
                "Musim non-puncak (sedikit supply = harga tinggi)",
                "Permintaan pasar lokal dan ekspor",
                "Biaya penyimpanan vs potensi kenaikan harga"
            ]
        }
    
    def process_query(self, query: str, context: Dict[str, Any] = None) -> str:
        """Main entry point for processing price queries."""
        context = context or {}
        return self.react_loop(query, context)
