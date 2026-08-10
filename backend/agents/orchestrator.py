"""
orchestrator.py — Agent Orchestrator
===================================
Central coordinator that manages all agents and their interactions.
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from .base_agent import AgentMessage, AgentState
from .memory import AgentMemory, FarmerContext, MemoryStore
from .weather_agent import WeatherAgent
from .price_agent import PriceAgent
from .farm_agent import FarmAgent
from .knowledge_agent import KnowledgeAgent
from .advisory_agent import AdvisoryAgent


class AgentOrchestrator:
    """
    Central coordinator for all agents.
    
    Responsibilities:
    - Route queries to appropriate agents
    - Manage agent communication
    - Coordinate multi-agent workflows
    - Aggregate and synthesize responses
    - Maintain farmer context
    """
    
    def __init__(self):
        self.storage = MemoryStore()
        self.agents = {}
        self.farmer_contexts = {}
        self.message_queue = []
        self._initialize_agents()
        
    def _initialize_agents(self):
        """Initialize all agents."""
        print("[Orchestrator] Initializing agents...")
        self.agents = {
            "weather": WeatherAgent(AgentMemory("weather_agent", self.storage)),
            "price": PriceAgent(AgentMemory("price_agent", self.storage)),
            "farm": FarmAgent(AgentMemory("farm_agent", self.storage)),
            "knowledge": KnowledgeAgent(AgentMemory("knowledge_agent", self.storage)),
            "advisory": AdvisoryAgent(AgentMemory("advisory_agent", self.storage)),
        }
        print(f"[Orchestrator] Initialized {len(self.agents)} agents")
    
    def process_query(self, query: str, farmer_id: str = "default", llm_mode: str = "local") -> Dict[str, Any]:
        """
        Process a query by routing to appropriate agent(s).
        """
        print(f"\n[Orchestrator] Processing query from farmer {farmer_id}: {query[:50]}...")
        
        # Get or create farmer context
        farmer_context = self._get_farmer_context(farmer_id)
        
        # Record the query
        farmer_context.add_query(query)
        
        # Determine which agents should handle this query
        relevant_agents = self._determine_relevant_agents(query)
        print(f"[Orchestrator] Relevant agents: {relevant_agents}")
        
        # Process query with primary agent
        responses = {}
        primary_agent = relevant_agents[0] if relevant_agents else "knowledge"
        
        context = {
            "farmer_id": farmer_id,
            "profile": farmer_context.get_profile(),
            "query": query,
            "llm_mode": llm_mode
        }
        
        # Get response from primary agent
        try:
            agent = self.agents.get(primary_agent)
            if agent:
                response = agent.process_query(query, context)
                responses[primary_agent] = response
                print(f"[Orchestrator] Primary agent ({primary_agent}) response: {response[:50]}...")
        except Exception as e:
            print(f"[Orchestrator] Error with {primary_agent}: {e}")
            responses[primary_agent] = f"Error: {str(e)}"
        
        # Get supplementary insights from advisory agent
        try:
            advisory = self.agents.get("advisory")
            if advisory and primary_agent != "advisory":
                advisory_insights = advisory.process_query(f"Provide advice for: {query}", context)
                responses["advisory"] = advisory_insights
        except Exception as e:
            print(f"[Orchestrator] Error with advisory: {e}")
        
        # Aggregate responses
        final_response = self._aggregate_responses(query, responses, context)
        
        return {
            "farmer_id": farmer_id,
            "query": query,
            "primary_agent": primary_agent,
            "response": final_response,
            "agent_responses": responses,
            "timestamp": datetime.now().isoformat()
        }
    
    def _determine_relevant_agents(self, query: str) -> List[str]:
        """Determine which agents are relevant for a query."""
        query_lower = query.lower()
        agent_scores = {}
        
        # Score each agent based on keyword matches
        keywords_map = {
            "weather": ["cuaca", "weather", "hujan", "panas", "dingin", "angin", "iklim"],
            "price": ["harga", "price", "jual", "beli", "pasar", "market", "pupuk", "benih"],
            "farm": ["tanam", "panen", "lahan", "jadwal", "rencana", "catat", "aktivitas", "padi"],
            "knowledge": ["hama", "penyakit", "pestisida", "obat", "panduan", "cara", "teknik", "tips"],
            "advisory": ["saran", "rekomendasi", "analisis", "insight", "optimal", "strategi"]
        }
        
        for agent, keywords in keywords_map.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > 0:
                agent_scores[agent] = score
        
        # Sort by score (descending) and return
        sorted_agents = sorted(agent_scores.items(), key=lambda x: x[1], reverse=True)
        
        if not sorted_agents:
            # Default to knowledge agent if no clear match
            return ["knowledge"]
        
        # Return top 3 relevant agents (limit to avoid overloading)
        return [agent for agent, score in sorted_agents[:3]]
    
    def _aggregate_responses(self, query: str, responses: Dict[str, str], context: Dict[str, Any]) -> str:
        """Aggregate responses from multiple agents."""
        if not responses:
            return "Maaf, tidak dapat memproses query Anda."
        
        # If only one response, return it directly
        if len(responses) == 1:
            return list(responses.values())[0]
        
        # Aggregate multiple responses
        primary_response = responses.get(list(responses.keys())[0], "")
        advisory_response = responses.get("advisory", "")
        
        aggregated = primary_response
        
        if advisory_response and advisory_response not in primary_response:
            aggregated += "\n\n" + advisory_response
        
        return aggregated
    
    def _get_farmer_context(self, farmer_id: str) -> FarmerContext:
        """Get or create farmer context."""
        if farmer_id not in self.farmer_contexts:
            self.farmer_contexts[farmer_id] = FarmerContext(farmer_id, self.storage)
        return self.farmer_contexts[farmer_id]
    
    def set_farmer_profile(self, farmer_id: str, profile: Dict[str, Any]) -> bool:
        """Set farmer profile."""
        try:
            context = self._get_farmer_context(farmer_id)
            context.update_profile(profile)
            return True
        except Exception as e:
            print(f"Error setting farmer profile: {e}")
            return False
    
    def get_farmer_profile(self, farmer_id: str) -> Dict[str, Any]:
        """Get farmer profile."""
        context = self._get_farmer_context(farmer_id)
        return context.get_profile()
    
    def execute_multi_agent_workflow(self, 
                                    workflow_steps: List[Dict[str, Any]], 
                                    farmer_id: str = "default") -> Dict[str, Any]:
        """
        Execute a complex workflow involving multiple agents.
        
        workflow_steps: List of dicts with 'agent', 'action', and 'params'
        Example:
        [
            {'agent': 'farm', 'action': 'create_plan', 'params': {'crop': 'padi', 'area': 1}},
            {'agent': 'weather', 'action': 'check', 'params': {'lokasi': 'Bogor'}},
            {'agent': 'knowledge', 'action': 'get_guidance', 'params': {'topic': 'padi'}}
        ]
        """
        print(f"\n[Orchestrator] Executing workflow with {len(workflow_steps)} steps for {farmer_id}")
        
        results = []
        context = self._get_farmer_context(farmer_id)
        
        for i, step in enumerate(workflow_steps):
            agent_name = step.get("agent")
            action = step.get("action")
            params = step.get("params", {})
            
            print(f"[Orchestrator] Step {i+1}: {agent_name}.{action}")
            
            agent = self.agents.get(agent_name)
            if not agent:
                results.append({
                    "step": i,
                    "agent": agent_name,
                    "action": action,
                    "error": "Agent not found"
                })
                continue
            
            try:
                # Execute the action
                result = self._execute_agent_action(agent, action, params, context)
                results.append({
                    "step": i,
                    "agent": agent_name,
                    "action": action,
                    "result": result,
                    "success": True
                })
            except Exception as e:
                print(f"[Orchestrator] Error in step {i}: {e}")
                results.append({
                    "step": i,
                    "agent": agent_name,
                    "action": action,
                    "error": str(e),
                    "success": False
                })
        
        return {
            "workflow_status": "complete",
            "total_steps": len(workflow_steps),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def _execute_agent_action(self, agent: Any, action: str, params: Dict[str, Any], 
                            context: FarmerContext) -> Any:
        """Execute a specific action on an agent using strict whitelist validation."""
        # Find the agent ID in our self.agents registry
        agent_id = next((k for k, v in self.agents.items() if v is agent), None)
        
        if not agent_id:
            raise ValueError("Unknown agent object")

        # Strict allowlist of methods
        ALLOWED_ACTIONS = {
            "weather": {"process_query", "check_weather_periodically"},
            "price": {"process_query", "get_price_forecast", "suggest_selling_time"},
            "farm": {"process_query", "create_planting_plan"},
            "knowledge": {"process_query", "get_expert_answer", "search_by_topic"},
            "advisory": {"process_query", "monitor_farmer"}
        }

        # Resolve potential action aliases
        action_map = {
            "check": "process_query",
            "create_plan": "create_planting_plan",
            "get_guidance": "search_by_topic",
            "get_forecast": "get_price_forecast"
        }
        
        resolved_action = action_map.get(action, action)
        
        # Check if the resolved action is allowed for this agent
        if resolved_action not in ALLOWED_ACTIONS.get(agent_id, set()):
            raise PermissionError(f"Action '{action}' is not allowed on agent '{agent_id}'")
            
        # Execute only the allowed method explicitly
        if not hasattr(agent, resolved_action):
            raise AttributeError(f"Agent '{agent_id}' has no method '{resolved_action}'")
            
        method = getattr(agent, resolved_action)
        
        # Security: ensure we are calling a callable method, not a property/attribute
        if not callable(method):
            raise TypeError(f"Method '{resolved_action}' on agent '{agent_id}' is not callable")
            
        # If it is process_query, map parameters correctly
        if resolved_action == "process_query":
            query = params.get("query", "")
            return method(query, {"farmer_id": context.farmer_id})
            
        return method(**params)
    
    def broadcast_alert(self, message: AgentMessage):
        """Broadcast an alert to all agents."""
        self.message_queue.append(message)
        
        # Process by relevant agents
        for agent_id, agent in self.agents.items():
            agent.add_message(message)
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents."""
        status = {
            "timestamp": datetime.now().isoformat(),
            "agents": {}
        }
        
        for agent_id, agent in self.agents.items():
            status["agents"][agent_id] = agent.get_summary()
        
        return status
    
    def get_orchestrator_summary(self) -> Dict[str, Any]:
        """Get orchestrator summary."""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_agents": len(self.agents),
            "active_agents": len([a for a in self.agents.values() if a.state != AgentState.IDLE]),
            "farmers_tracked": len(self.farmer_contexts),
            "message_queue_size": len(self.message_queue),
            "agents": list(self.agents.keys())
        }
    
    def monitor_all_farmers(self) -> List[AgentMessage]:
        """Monitor all farmers and generate alerts if needed."""
        alerts = []
        
        for farmer_id, context in self.farmer_contexts.items():
            # Get advisory agent to monitor
            advisory = self.agents.get("advisory")
            if advisory:
                alert = advisory.monitor_farmer(farmer_id)
                if alert:
                    alerts.append(alert)
        
        return alerts
