"""
base_agent.py — Abstract Agent Base Class
==========================================
Defines the core interface for all agents in the Tani-Cerdas system.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


class AgentState(Enum):
    """Agent operational states."""
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    OBSERVING = "observing"
    ERROR = "error"
    COMPLETE = "complete"


@dataclass
class AgentMessage:
    """Structured message format for inter-agent communication."""
    sender: str  # Agent ID
    recipient: str  # "broadcast" or specific agent ID
    intent: str  # "query", "action", "response", "alert"
    content: str
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


class Agent(ABC):
    """
    Abstract base class for all agents in the system.
    Each agent has:
    - Specialized role and tools
    - Independent memory
    - Communication capability
    - Planning and reasoning
    """
    
    def __init__(
        self, 
        agent_id: str, 
        name: str, 
        description: str,
        memory=None
    ):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.state = AgentState.IDLE
        self.memory = memory or {}
        self.message_queue = []
        self.last_action = None
        self.iteration_count = 0
        self.max_iterations = 3
        
    @abstractmethod
    def process_query(self, query: str, context: Dict[str, Any] = None) -> str:
        """
        Process a query and return a response.
        This is the main entry point for the agent.
        """
        pass
    
    @abstractmethod
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Return list of available tools with descriptions."""
        pass
    
    @abstractmethod
    def plan(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a plan for handling the query.
        Returns plan with steps, required tools, and strategy.
        """
        pass
    
    @abstractmethod
    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Execute a specific tool with given parameters."""
        pass
    
    @abstractmethod
    def reason(self, observations: Dict[str, Any]) -> str:
        """Reason about observations and generate response."""
        pass
    
    def add_message(self, message: AgentMessage):
        """Add a message to the agent's inbox."""
        self.message_queue.append(message)
    
    def get_messages(self) -> List[AgentMessage]:
        """Retrieve all pending messages."""
        messages = self.message_queue
        self.message_queue = []
        return messages
    
    def broadcast_message(self, intent: str, content: str, payload: Dict = None):
        """Send a message to all agents."""
        message = AgentMessage(
            sender=self.agent_id,
            recipient="broadcast",
            intent=intent,
            content=content,
            payload=payload or {}
        )
        return message
    
    def set_state(self, state: AgentState):
        """Update agent state."""
        self.state = state
    
    def save_memory(self, key: str, value: Any):
        """Save information to agent memory."""
        self.memory[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
    
    def recall_memory(self, key: str) -> Optional[Any]:
        """Retrieve information from agent memory."""
        if key in self.memory:
            return self.memory[key].get("value")
        return None
    
    def clear_memory(self):
        """Clear all agent memory."""
        self.memory = {}
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the agent's current state."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "state": self.state.value,
            "iteration_count": self.iteration_count,
            "last_action": self.last_action,
            "memory_keys": list(self.memory.keys())
        }


class ReactAgent(Agent):
    """
    Implements Reasoning + Acting (ReAct) pattern.
    Agents think, act, and observe in a loop.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reasoning_history = []
        
    def react_loop(self, query: str, context: Dict[str, Any] = None) -> str:
        """
        Execute ReAct loop:
        1. Think (reason about the query)
        2. Act (use tools if needed)
        3. Observe (check results)
        4. Return final answer or repeat
        """
        context = context or {}
        self.set_state(AgentState.THINKING)
        
        for i in range(self.max_iterations):
            self.iteration_count = i + 1
            
            # Thinking phase
            plan = self.plan(query, context)
            thought = f"Iteration {i+1}: {plan.get('reasoning', '')}"
            self.reasoning_history.append(thought)
            
            # Check if action is needed
            if plan.get("needs_action", False):
                self.set_state(AgentState.ACTING)
                tool_name = plan.get("tool")
                tool_params = plan.get("tool_params", {})
                
                try:
                    observation = self.execute_tool(tool_name, tool_params)
                    self.set_state(AgentState.OBSERVING)
                    context["last_observation"] = observation
                except Exception as e:
                    context["last_error"] = str(e)
                    self.set_state(AgentState.ERROR)
            else:
                # Can answer directly
                break
        
        # Reasoning phase - generate final answer
        self.set_state(AgentState.THINKING)
        response = self.reason(context)
        self.set_state(AgentState.COMPLETE)
        
        return response


class PlanningAgent(Agent):
    """
    Agent that uses explicit planning before execution.
    Good for complex multi-step tasks.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_plan = None
        self.completed_steps = []
        
    def planning_loop(self, query: str, context: Dict[str, Any] = None) -> str:
        """
        Execute planning loop:
        1. Create a detailed plan
        2. Execute steps sequentially
        3. Adapt based on results
        4. Return comprehensive response
        """
        context = context or {}
        self.set_state(AgentState.THINKING)
        
        # Create comprehensive plan
        self.current_plan = self.plan(query, context)
        steps = self.current_plan.get("steps", [])
        
        # Execute steps
        for step in steps:
            step_name = step.get("name", "")
            tool_name = step.get("tool", "")
            tool_params = step.get("params", {})
            
            self.set_state(AgentState.ACTING)
            try:
                result = self.execute_tool(tool_name, tool_params)
                self.completed_steps.append({
                    "step": step_name,
                    "result": result,
                    "success": True
                })
                context[f"step_result_{len(self.completed_steps)-1}"] = result
            except Exception as e:
                self.set_state(AgentState.ERROR)
                self.completed_steps.append({
                    "step": step_name,
                    "error": str(e),
                    "success": False
                })
                # Decide if we should continue or abort
                if step.get("critical", False):
                    break
        
        # Reason about all results
        context["completed_steps"] = self.completed_steps
        response = self.reason(context)
        self.set_state(AgentState.COMPLETE)
        
        return response
