"""
farm_agent.py — Farm Agent
=========================
Specialized agent for farm planning, scheduling, and record management.
"""

from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta
from .base_agent import PlanningAgent, AgentMessage
from .memory import AgentMemory


class FarmAgent(PlanningAgent):
    """
    Farm Agent - Manages farm planning and agricultural records.
    
    Responsibilities:
    - Crop planting schedules
    - Field management
    - Input tracking (seeds, fertilizer, water)
    - Harvest planning
    - Multi-field coordination
    """
    
    def __init__(self, memory: Optional[AgentMemory] = None):
        super().__init__(
            agent_id="farm_agent",
            name="Farm Agent",
            description="Manages farm planning, scheduling, and records",
            memory=memory or AgentMemory("farm_agent")
        )
        self.crop_data = {
            "padi": {"duration": 120, "season": "wet", "water_need": "high"},
            "jagung": {"duration": 90, "season": "dry", "water_need": "medium"},
            "cabai": {"duration": 150, "season": "dry", "water_need": "medium"},
            "bawang": {"duration": 90, "season": "dry", "water_need": "low"},
        }
        
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Return available tools."""
        return [
            {
                "name": "plan_planting",
                "description": "Plan crop planting schedule",
                "params": ["crop", "area_size"]
            },
            {
                "name": "record_activity",
                "description": "Record farm activity",
                "params": ["activity_type", "date", "details"]
            }
        ]
    
    def plan(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a comprehensive farm planning."""
        # Parse query for intent
        is_planting = "tanam" in query.lower() or "rencana" in query.lower()
        is_schedule = "jadwal" in query.lower() or "kapan" in query.lower()
        is_record = "catat" in query.lower() or "hasil" in query.lower()
        
        plan = {
            "reasoning": f"Farm planning query - planting: {is_planting}, schedule: {is_schedule}, record: {is_record}",
            "steps": []
        }
        
        if is_planting:
            plan["steps"].append({
                "name": "get_crop_info",
                "tool": "get_crop_requirements",
                "params": {"query": query},
                "critical": True
            })
            plan["steps"].append({
                "name": "calculate_schedule",
                "tool": "calculate_planting_schedule",
                "params": {"query": query},
                "critical": True
            })
        
        if is_record:
            plan["steps"].append({
                "name": "record_activity",
                "tool": "record_activity",
                "params": {"query": query},
                "critical": False
            })
        
        return plan
    
    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Execute a farm management tool."""
        if tool_name == "get_crop_requirements":
            return self._get_crop_requirements(params.get("query", ""))
        elif tool_name == "calculate_planting_schedule":
            return self._calculate_planting_schedule(params.get("query", ""))
        elif tool_name == "record_activity":
            return self._record_farm_activity(params.get("query", ""))
        return {"error": f"Unknown tool: {tool_name}"}
    
    def _get_crop_requirements(self, query: str) -> Dict[str, Any]:
        """Get crop requirements from knowledge base."""
        for crop, data in self.crop_data.items():
            if crop in query.lower():
                return {
                    "crop": crop,
                    "duration_days": data["duration"],
                    "season": data["season"],
                    "water_requirement": data["water_need"],
                    "timestamp": datetime.now().isoformat()
                }
        return {"error": "Tanaman tidak dikenali"}
    
    def _calculate_planting_schedule(self, query: str) -> Dict[str, Any]:
        """Calculate optimal planting schedule."""
        today = datetime.now()
        schedule = {
            "start_date": today.strftime("%Y-%m-%d"),
            "milestones": []
        }
        
        # Find crop
        crop = None
        for c in self.crop_data.keys():
            if c in query.lower():
                crop = c
                break
        
        if crop:
            duration = self.crop_data[crop]["duration"]
            schedule["milestones"] = [
                {
                    "day": 0,
                    "activity": "Persiapan lahan dan penanaman",
                    "date": today.strftime("%Y-%m-%d")
                },
                {
                    "day": 30,
                    "activity": "Pemupukan pertama",
                    "date": (today + timedelta(days=30)).strftime("%Y-%m-%d")
                },
                {
                    "day": 60,
                    "activity": "Pemupukan kedua dan monitoring hama",
                    "date": (today + timedelta(days=60)).strftime("%Y-%m-%d")
                },
                {
                    "day": duration,
                    "activity": "Panen",
                    "date": (today + timedelta(days=duration)).strftime("%Y-%m-%d")
                }
            ]
        
        return schedule
    
    def _record_farm_activity(self, query: str) -> Dict[str, Any]:
        """Record a farm activity."""
        activity = {
            "type": "general",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "description": query,
            "timestamp": datetime.now().isoformat()
        }
        
        # Categorize activity
        if "pupuk" in query.lower():
            activity["type"] = "fertilizer"
        elif "air" in query.lower() or "siram" in query.lower():
            activity["type"] = "irrigation"
        elif "hama" in query.lower() or "penyakit" in query.lower():
            activity["type"] = "pest_management"
        elif "panen" in query.lower():
            activity["type"] = "harvest"
        
        # Save to memory
        self.memory.remember(f"activity_{datetime.now().timestamp()}", activity, persistent=True)
        
        return activity
    
    def reason(self, observations: Dict[str, Any]) -> str:
        """Generate comprehensive farm planning response."""
        steps = observations.get("completed_steps", [])
        
        if not steps:
            return "Tidak dapat membuat rencana pertanian. Silakan coba lagi."
        
        response = "📋 Rencana Pertanian Anda:\n"
        response += "=" * 50 + "\n\n"
        
        for i, step in enumerate(steps, 1):
            if step.get("success"):
                result = step.get("result", {})
                step_name = step.get("step", f"Step {i}")
                
                response += f"✓ {step_name}\n"
                
                # Format based on step type
                if "crop" in result:
                    response += f"  Tanaman: {result['crop'].title()}\n"
                    response += f"  Durasi: {result.get('duration_days', 'N/A')} hari\n"
                    response += f"  Musim: {result.get('season', 'N/A')}\n"
                    response += f"  Kebutuhan Air: {result.get('water_requirement', 'N/A')}\n"
                
                if "milestones" in result:
                    response += "  Jadwal:\n"
                    for milestone in result.get("milestones", []):
                        response += f"    - {milestone.get('date')}: {milestone.get('activity')}\n"
                
                response += "\n"
        
        response += "=" * 50 + "\n"
        response += "💡 Tips:\n"
        response += "• Catat setiap aktivitas pertanian untuk monitoring\n"
        response += "• Ikuti jadwal pemupukan dan penyiraman\n"
        response += "• Siapkan tindakan antisipasi hama sebelumnya\n"
        
        return response
    
    def create_planting_plan(self, crop: str, area_size: float, location: str) -> Dict[str, Any]:
        """Create a detailed planting plan."""
        plan = {
            "crop": crop,
            "area_size": area_size,
            "location": location,
            "created_at": datetime.now().isoformat(),
            "details": self._get_crop_requirements(crop),
            "schedule": self._calculate_planting_schedule(crop),
            "input_requirements": self._calculate_input_needs(crop, area_size),
            "expected_yield": self._estimate_yield(crop, area_size)
        }
        
        self.memory.remember(f"plan_{crop}_{datetime.now().timestamp()}", plan, persistent=True)
        return plan
    
    def _calculate_input_needs(self, crop: str, area_size: float) -> Dict[str, float]:
        """Calculate fertilizer and seed requirements."""
        input_needs = {
            "seeds_kg": area_size * 20,  # Simplified
            "urea_kg": area_size * 50,
            "npk_kg": area_size * 50,
            "water_mm": 1000,  # mm for growing season
        }
        return input_needs
    
    def _estimate_yield(self, crop: str, area_size: float) -> Dict[str, Any]:
        """Estimate yield based on crop and area."""
        yields_per_hectare = {
            "padi": 5000,  # kg
            "jagung": 4000,
            "cabai": 2000,
            "bawang": 1500,
        }
        
        kg_per_hectare = yields_per_hectare.get(crop, 1000)
        expected = (area_size * kg_per_hectare) / 10000  # area_size in are (100m2)
        
        return {
            "crop": crop,
            "estimated_yield_kg": expected,
            "confidence": "medium",
            "factors": ["cuaca", "kesuburan tanah", "manajemen hama", "irigasi"]
        }
    
    def process_query(self, query: str, context: Dict[str, Any] = None) -> str:
        """Main entry point for processing farm queries."""
        context = context or {}
        return self.planning_loop(query, context)
