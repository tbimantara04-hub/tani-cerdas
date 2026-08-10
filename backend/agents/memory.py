"""
memory.py — Agent Memory System
==============================
Provides persistent memory for agents with short/long-term storage.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from pathlib import Path


class MemoryStore:
    """In-memory storage with JSON persistence."""
    
    def __init__(self, storage_dir: str = "storage/agent_memory"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.cache = {}
        self.dirty = {}  # Track which files need to be saved
        
    def _get_file_path(self, key: str) -> Path:
        """Get file path for a memory key."""
        return self.storage_dir / f"{key}.json"
    
    def save(self, key: str, data: Dict[str, Any]):
        """Save data to memory store."""
        try:
            file_path = self._get_file_path(key)
            data["_timestamp"] = datetime.now().isoformat()
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.cache[key] = data
            return True
        except Exception as e:
            print(f"Error saving memory {key}: {e}")
            return False
    
    def load(self, key: str) -> Optional[Dict[str, Any]]:
        """Load data from memory store."""
        if key in self.cache:
            return self.cache[key]
        
        try:
            file_path = self._get_file_path(key)
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.cache[key] = data
                return data
        except Exception as e:
            print(f"Error loading memory {key}: {e}")
        
        return None
    
    def delete(self, key: str) -> bool:
        """Delete a memory entry."""
        try:
            file_path = self._get_file_path(key)
            if file_path.exists():
                file_path.unlink()
            if key in self.cache:
                del self.cache[key]
            return True
        except Exception as e:
            print(f"Error deleting memory {key}: {e}")
            return False
    
    def list_keys(self) -> List[str]:
        """List all stored memory keys."""
        return [f.stem for f in self.storage_dir.glob("*.json")]


class AgentMemory:
    """
    Agent-specific memory system with short-term and long-term storage.
    - Short-term: Working memory for current task (up to 10 items)
    - Long-term: Persistent memory of patterns and learnings
    - Context-specific: Indexed by context/farmer
    """
    
    def __init__(self, agent_id: str, storage: Optional[MemoryStore] = None):
        self.agent_id = agent_id
        self.storage = storage or MemoryStore()
        self.short_term = {}  # Working memory
        self.max_short_term = 10
        self._load_persistent_memory()
        
    def _load_persistent_memory(self):
        """Load agent's persistent memory from storage."""
        key = f"agent_{self.agent_id}_memory"
        self.long_term = self.storage.load(key) or {
            "observations": [],
            "patterns": [],
            "learnings": [],
            "context_history": []
        }
    
    def _save_persistent_memory(self):
        """Save agent's persistent memory to storage."""
        key = f"agent_{self.agent_id}_memory"
        self.storage.save(key, self.long_term)
    
    def remember(self, key: str, value: Any, persistent: bool = False):
        """
        Store information.
        persistent=True saves to long-term memory.
        """
        if persistent:
            if "custom" not in self.long_term:
                self.long_term["custom"] = {}
            self.long_term["custom"][key] = {
                "value": value,
                "timestamp": datetime.now().isoformat()
            }
            self._save_persistent_memory()
        else:
            self.short_term[key] = {
                "value": value,
                "timestamp": datetime.now().isoformat()
            }
            # Keep short-term bounded
            if len(self.short_term) > self.max_short_term:
                oldest = min(self.short_term.items(), 
                           key=lambda x: x[1]["timestamp"])
                del self.short_term[oldest[0]]
    
    def recall(self, key: str) -> Optional[Any]:
        """Retrieve information from memory."""
        # Check short-term first
        if key in self.short_term:
            return self.short_term[key]["value"]
        
        # Check long-term
        if "custom" in self.long_term and key in self.long_term["custom"]:
            return self.long_term["custom"][key]["value"]
        
        return None
    
    def forget(self, key: str):
        """Remove information from memory."""
        if key in self.short_term:
            del self.short_term[key]
    
    def record_observation(self, observation: Dict[str, Any]):
        """Record an observation for pattern learning."""
        self.long_term["observations"].append({
            "data": observation,
            "timestamp": datetime.now().isoformat()
        })
        # Keep only recent observations (last 100)
        if len(self.long_term["observations"]) > 100:
            self.long_term["observations"] = self.long_term["observations"][-100:]
        self._save_persistent_memory()
    
    def add_pattern(self, pattern: Dict[str, Any]):
        """Record a learned pattern."""
        self.long_term["patterns"].append({
            "pattern": pattern,
            "discovered": datetime.now().isoformat()
        })
        self._save_persistent_memory()
    
    def get_patterns(self) -> List[Dict[str, Any]]:
        """Retrieve all learned patterns."""
        return self.long_term.get("patterns", [])
    
    def add_learning(self, learning: str):
        """Record a learning/insight."""
        self.long_term["learnings"].append({
            "insight": learning,
            "timestamp": datetime.now().isoformat()
        })
        self._save_persistent_memory()
    
    def get_learnings(self) -> List[str]:
        """Retrieve all learnings."""
        return [l["insight"] for l in self.long_term.get("learnings", [])]
    
    def add_context_history(self, farmer_id: str, context: Dict[str, Any]):
        """Store farmer-specific context history."""
        self.long_term["context_history"].append({
            "farmer_id": farmer_id,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })
        # Keep last 50 contexts
        if len(self.long_term["context_history"]) > 50:
            self.long_term["context_history"] = self.long_term["context_history"][-50:]
        self._save_persistent_memory()
    
    def get_farmer_context_history(self, farmer_id: str) -> List[Dict[str, Any]]:
        """Get history of a specific farmer's contexts."""
        return [
            h for h in self.long_term.get("context_history", [])
            if h.get("farmer_id") == farmer_id
        ]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get memory summary for debugging."""
        return {
            "agent_id": self.agent_id,
            "short_term_size": len(self.short_term),
            "observations_count": len(self.long_term.get("observations", [])),
            "patterns_count": len(self.long_term.get("patterns", [])),
            "learnings_count": len(self.long_term.get("learnings", [])),
            "context_history_count": len(self.long_term.get("context_history", []))
        }
    
    def clear(self):
        """Clear all memory."""
        self.short_term = {}
        self.long_term = {
            "observations": [],
            "patterns": [],
            "learnings": [],
            "context_history": []
        }
        self._save_persistent_memory()


class FarmerContext:
    """Manages farmer-specific context across all agents."""
    
    def __init__(self, farmer_id: str, storage: Optional[MemoryStore] = None):
        self.farmer_id = farmer_id
        self.storage = storage or MemoryStore()
        self.context = self._load_context()
        
    def _load_context(self) -> Dict[str, Any]:
        """Load farmer context from storage."""
        key = f"farmer_{self.farmer_id}_context"
        return self.storage.load(key) or {
            "farmer_id": self.farmer_id,
            "profile": {},
            "recent_queries": [],
            "concerns": [],
            "achievements": [],
            "created_at": datetime.now().isoformat()
        }
    
    def _save_context(self):
        """Save farmer context to storage."""
        key = f"farmer_{self.farmer_id}_context"
        self.context["updated_at"] = datetime.now().isoformat()
        self.storage.save(key, self.context)
    
    def update_profile(self, profile: Dict[str, Any]):
        """Update farmer profile (crop, land size, location, etc)."""
        self.context["profile"].update(profile)
        self._save_context()
    
    def get_profile(self) -> Dict[str, Any]:
        """Get farmer profile."""
        return self.context.get("profile", {})
    
    def add_query(self, query: str):
        """Record a query."""
        self.context["recent_queries"].append({
            "query": query,
            "timestamp": datetime.now().isoformat()
        })
        # Keep last 50 queries
        if len(self.context["recent_queries"]) > 50:
            self.context["recent_queries"] = self.context["recent_queries"][-50:]
        self._save_context()
    
    def add_concern(self, concern: Dict[str, Any]):
        """Record a concern (pest, disease, resource issue, etc)."""
        self.context["concerns"].append({
            "concern": concern,
            "timestamp": datetime.now().isoformat()
        })
        self._save_context()
    
    def get_recent_concerns(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get recent concerns within specified days."""
        cutoff = datetime.now() - timedelta(days=days)
        return [
            c for c in self.context.get("concerns", [])
            if datetime.fromisoformat(c["timestamp"]) > cutoff
        ]
    
    def record_achievement(self, achievement: Dict[str, Any]):
        """Record a successful outcome or achievement."""
        self.context["achievements"].append({
            "achievement": achievement,
            "timestamp": datetime.now().isoformat()
        })
        self._save_context()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get context summary."""
        return {
            "farmer_id": self.farmer_id,
            "profile": self.context.get("profile", {}),
            "recent_queries_count": len(self.context.get("recent_queries", [])),
            "active_concerns": len(self.context.get("concerns", [])),
            "achievements": len(self.context.get("achievements", []))
        }
