"""
weather_agent.py — Weather Agent
================================
Specialized agent for weather monitoring, forecasting, and alerts.
"""

import json
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from .base_agent import ReactAgent, AgentState, AgentMessage
from .memory import AgentMemory
from .tools_enhanced import get_tool


class WeatherAgent(ReactAgent):
    """
    Weather Agent - Handles all weather-related queries and monitoring.
    
    Responsibilities:
    - Real-time weather checks
    - Weather alerts for critical conditions
    - Seasonal pattern recognition
    - Crop-specific weather recommendations
    """
    
    def __init__(self, memory: Optional[AgentMemory] = None):
        super().__init__(
            agent_id="weather_agent",
            name="Weather Agent",
            description="Monitors and provides weather information and alerts",
            memory=memory or AgentMemory("weather_agent")
        )
        self.weather_tool = get_tool("cek_cuaca")
        self.thresholds = {
            "extreme_heat": 35,  # Celsius
            "extreme_cold": 10,
            "high_humidity": 85,
            "strong_wind": 20  # km/h
        }
        
    def get_available_tools(self) -> list[Dict[str, Any]]:
        """Return available tools."""
        return [
            {
                "name": "cek_cuaca",
                "description": "Get real-time weather data",
                "params": ["lokasi"]
            }
        ]
    
    def plan(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Plan weather query handling."""
        # Extract location from context or query
        lokasi = context.get("lokasi") or self._extract_location(query)
        if not lokasi:
            lokasi = "Jakarta"
        
        # Determine if we need to check thresholds
        check_alerts = "alert" in query.lower() or "danger" in query.lower()
        
        plan = {
            "reasoning": f"Checking weather for {lokasi}, checking alerts: {check_alerts}",
            "needs_action": True,
            "tool": "cek_cuaca",
            "tool_params": {"lokasi": lokasi},
            "check_thresholds": check_alerts
        }
        
        return plan
    
    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Execute a weather tool."""
        if tool_name == "cek_cuaca":
            result = self.weather_tool.execute(**params)
            # Store in memory for pattern analysis
            if result.get("success"):
                lokasi = params.get("lokasi", "")
                self.memory.remember(f"last_weather_{lokasi}", result, persistent=True)
            return result
        return {"error": f"Unknown tool: {tool_name}"}
    
    def reason(self, observations: Dict[str, Any]) -> str:
        """Reason about weather observations and generate recommendations."""
        if "last_observation" not in observations:
            return "Tidak dapat mengambil data cuaca. Silakan coba lagi."
        
        weather_data = observations["last_observation"]
        
        if not weather_data.get("success"):
            return f"Gagal mengecek cuaca: {weather_data.get('error', 'Unknown error')}"
        
        # Generate response with analysis
        temp = weather_data.get("temperature", 0)
        humidity = weather_data.get("humidity", 0)
        condition = weather_data.get("condition", "")
        wind_speed = weather_data.get("wind_speed", 0)
        lokasi = weather_data.get("location", "")
        
        response = f"📍 Cuaca di {lokasi}:\n"
        response += f"🌡️ Suhu: {temp}°C (terasa {weather_data.get('feels_like', temp)}°C)\n"
        response += f"💨 Angin: {wind_speed} km/h\n"
        response += f"💧 Kelembaban: {humidity}%\n"
        response += f"🌦️ Kondisi: {condition}\n\n"
        
        # Check for alerts
        alerts = self._check_weather_alerts(weather_data)
        if alerts:
            response += "⚠️ PERINGATAN:\n"
            for alert in alerts:
                response += f"• {alert}\n"
            response += "\n"
        
        # Provide agricultural recommendations
        recommendations = self._get_crop_recommendations(weather_data, observations.get("crop_type"))
        if recommendations:
            response += "🌾 Rekomendasi:\n"
            for rec in recommendations:
                response += f"• {rec}\n"
        
        return response
    
    def _extract_location(self, query: str) -> Optional[str]:
        """Extract location from query."""
        # Simple extraction - can be enhanced with NER
        keywords = ["di ", "untuk ", "lokasi "]
        for kw in keywords:
            if kw in query.lower():
                parts = query.lower().split(kw)
                if len(parts) > 1:
                    return parts[1].split()[0].title()
        return None
    
    def _check_weather_alerts(self, weather_data: Dict[str, Any]) -> list[str]:
        """Check if weather conditions trigger alerts."""
        alerts = []
        
        temp = weather_data.get("temperature", 0)
        humidity = weather_data.get("humidity", 0)
        wind_speed = weather_data.get("wind_speed", 0)
        
        if temp > self.thresholds["extreme_heat"]:
            alerts.append(f"Suhu sangat panas ({temp}°C). Pastikan tanaman disiram cukup dan berikan naungan.")
        
        if temp < self.thresholds["extreme_cold"]:
            alerts.append(f"Suhu sangat dingin ({temp}°C). Lindungi tanaman sensitif dari frost.")
        
        if humidity > self.thresholds["high_humidity"]:
            alerts.append(f"Kelembaban sangat tinggi ({humidity}%). Risiko penyakit jamur meningkat.")
        
        if wind_speed > self.thresholds["strong_wind"]:
            alerts.append(f"Angin kuat ({wind_speed} km/h). Perhatian pada tanaman muda dan struktur.")
        
        return alerts
    
    def _get_crop_recommendations(self, weather_data: Dict[str, Any], crop_type: Optional[str] = None) -> list[str]:
        """Get crop-specific recommendations based on weather."""
        recommendations = []
        
        condition = weather_data.get("condition", "").lower()
        temp = weather_data.get("temperature", 0)
        humidity = weather_data.get("humidity", 0)
        
        # Generic recommendations
        if "rain" in condition or "hujan" in condition:
            recommendations.append("Cuaca hujan - tunda penyemprotan pestisida/pupuk")
            recommendations.append("Pastikan sistem drainase berfungsi baik")
        elif "sunny" in condition or "cerah" in condition:
            recommendations.append("Cuaca cerah - pastikan tanaman cukup air")
        
        if temp > 30:
            recommendations.append("Hari panas - tingkatkan frekuensi penyiraman")
        
        if humidity < 40:
            recommendations.append("Udara kering - risiko serangan tungau meningkat, monitor tanaman")
        
        return recommendations
    
    def check_weather_periodically(self, locations: list[str]):
        """Monitor weather for multiple locations."""
        for lokasi in locations:
            result = self.weather_tool.execute(lokasi=lokasi)
            if result.get("success"):
                # Check for alerts and notify
                alerts = self._check_weather_alerts(result)
                if alerts:
                    message = AgentMessage(
                        sender=self.agent_id,
                        recipient="broadcast",
                        intent="alert",
                        content=f"Weather alert for {lokasi}",
                        payload={
                            "location": lokasi,
                            "alerts": alerts,
                            "weather_data": result
                        }
                    )
                    # Store for broadcasting
                    self.save_memory(f"alert_{lokasi}", message)
    
    def process_query(self, query: str, context: Dict[str, Any] = None) -> str:
        """Main entry point for processing weather queries."""
        context = context or {}
        return self.react_loop(query, context)
