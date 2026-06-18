"""
Simple Agent Blackboard for VoltStream Multi-Agent System.

Provides minimal shared state between agents without complex event systems.
All implementation stays within the /agent folder as required.
"""

import threading
from typing import Dict, List, Any, Optional


class AgentBlackboard:
    """
    Simple in-memory blackboard for agent coordination.
    
    Features:
    - Thread-safe using simple locking
    - Minimal shared state
    - No event bus or complex synchronization
    - Singleton pattern
    """
    
    def __init__(self):
        """Initialize blackboard with empty state."""
        self._state = {
            "device_states": {},           # device_id -> state
            "energy_metrics": {},          # metric_name -> value
            "recent_actions": [],          # List of recent actions (max 10)
        }
        self._lock = threading.Lock()
    
    def update_device_state(self, device_id: int, state: str, metadata: Optional[Dict] = None) -> None:
        """Update device state in blackboard."""
        with self._lock:
            self._state["device_states"][device_id] = {
                "state": state,
                "metadata": metadata or {}
            }
            # Keep only last 10 states to prevent memory growth
            if len(self._state["device_states"]) > 10:
                # Remove oldest entries (simple approach)
                oldest_key = next(iter(self._state["device_states"]))
                self._state["device_states"].pop(oldest_key, None)
    
    def get_device_state(self, device_id: int) -> Optional[Dict[str, Any]]:
        """Get device state from blackboard."""
        with self._lock:
            return self._state["device_states"].get(device_id)
    
    def get_all_device_states(self) -> Dict[int, Dict[str, Any]]:
        """Get all device states."""
        with self._lock:
            return self._state["device_states"].copy()
    
    def update_energy_metrics(self, metrics: Dict[str, Any]) -> None:
        """Update energy metrics in blackboard."""
        with self._lock:
            self._state["energy_metrics"].update(metrics)
    
    def get_energy_metrics(self) -> Dict[str, Any]:
        """Get all energy metrics."""
        with self._lock:
            return self._state["energy_metrics"].copy()
    
    def add_action(self, action_data: Dict[str, Any]) -> None:
        """Add action to recent actions list."""
        with self._lock:
            self._state["recent_actions"].append(action_data)
            # Keep only last 10 actions
            if len(self._state["recent_actions"]) > 10:
                self._state["recent_actions"] = self._state["recent_actions"][-10:]
    
    def get_recent_actions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent actions with optional limit."""
        with self._lock:
            return self._state["recent_actions"][-limit:] if limit else self._state["recent_actions"].copy()
    
    def clear(self) -> None:
        """Clear all blackboard data."""
        with self._lock:
            self._state = {
                "device_states": {},
                "energy_metrics": {},
                "recent_actions": []
            }
    
    def get_state(self) -> Dict[str, Any]:
        """Get complete blackboard state (for debugging)."""
        with self._lock:
            return {
                "device_states": self._state["device_states"].copy(),
                "energy_metrics": self._state["energy_metrics"].copy(),
                "recent_actions": self._state["recent_actions"].copy()
            }


# Singleton instance
_blackboard_instance: Optional[AgentBlackboard] = None


def get_blackboard() -> AgentBlackboard:
    """
    Get the shared blackboard instance.
    
    Returns:
        Shared AgentBlackboard instance
    """
    global _blackboard_instance
    if _blackboard_instance is None:
        _blackboard_instance = AgentBlackboard()
    return _blackboard_instance