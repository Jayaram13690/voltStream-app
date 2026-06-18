"""
Simple Multi-Agent Coordinator for VoltStream.

Provides basic routing between Device and Energy agents without complex
workflows, event buses, or supervisor patterns.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List

from app.agent.agent_service import get_device_agent
from app.agent.energy_advisor_service import get_energy_advisor
from app.agent.agent_blackboard import get_blackboard

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentCoordinator:
    """
    Simple coordinator for multi-agent system.
    
    Responsibilities:
    - Route requests to appropriate agents
    - Aggregate responses
    - Update shared blackboard
    - No complex workflows or event systems
    """
    
    def __init__(self):
        """Initialize coordinator with agent references."""
        self.device_agent = get_device_agent()
        self.energy_agent = get_energy_advisor()
        self.blackboard = get_blackboard()
        
        logger.info("AgentCoordinator initialized")
    

    
    def _determine_route(self, user_input: str) -> str:
        """
        Improved keyword-based routing with better disambiguation.
        
        Args:
            user_input: User's natural language request
            
        Returns:
            'device', 'energy', or 'both'
        """
        input_lower = user_input.lower()
        
        # Device-related keywords - more specific patterns
        device_patterns = [
            'turn on', 'turn off', 'toggle', 'switch',
            'ac ', 'heat pump', 'fan ', 'light ', 'device '
        ]
        
        # Energy-related keywords - more specific patterns  
        energy_patterns = [
            'energy ', 'bill ', 'cost ', 'save ', 'optimize ',
            'solar ', 'budget ', 'consumption ', 'usage '
        ]
        
        # Words that suggest combined operations
        combined_words = ['and ', 'with ', 'also ', 'then ']
        
        # Check for device-only requests (more precise matching)
        is_device_only = any(pattern in input_lower for pattern in device_patterns)
        
        # Check for energy-only requests
        is_energy_only = any(pattern in input_lower for pattern in energy_patterns)
        
        # Check for combined operation words
        has_combined_words = any(word in input_lower for word in combined_words)
        
        # Improved routing logic
        if is_device_only and not is_energy_only:
            return 'device'
        elif is_energy_only and not is_device_only:
            # For now, keep energy-only requests as energy-only
            # The test case "optimize my house for energy savings" should actually be energy-only
            # since it doesn't mention any specific devices to control
            return 'energy'
        elif is_device_only and is_energy_only:
            return 'both'
        else:
            # Default to both for general queries or when unsure
            return 'both'
    
    def process_request(self, user_input: str) -> Dict[str, Any]:
        """
        Main entry point for multi-agent processing.
        
        Args:
            user_input: User's natural language request
            
        Returns:
            {
                "response": str,
                "agents_used": List[str],
                "success": bool
            }
        """
        logger.info(f"Processing request: {user_input}")
        
        route = self._determine_route(user_input)
        agents_used = []
        final_response = ""
        
        try:
            if route == 'device':
                # Device-only request
                response = self.device_agent.process_request(user_input)
                final_response = response
                agents_used = ['device']
                
            elif route == 'energy':
                # Energy-only request  
                response = self.energy_agent.process_request(user_input)
                final_response = response
                agents_used = ['energy']
                
            else:  # route == 'both'
                # Combined request: device first, then energy
                device_response = self.device_agent.process_request(user_input)
                
                energy_response = self.energy_agent.process_request(user_input)
                
                # Simple response aggregation
                final_response = f"{device_response}\n\n{energy_response}"
                agents_used = ['device', 'energy']
                
            return {
                "response": final_response,
                "agents_used": agents_used,
                "success": True
            }
                
        except Exception as e:
            logger.error(f"Error processing request: {e}", exc_info=True)
            return {
                "response": f"An error occurred while processing your request: {str(e)}",
                "agents_used": agents_used,
                "success": False
            }


# Singleton instance
_coordinator_instance: AgentCoordinator = None


def get_coordinator() -> AgentCoordinator:
    """
    Get the shared coordinator instance.
    
    Returns:
        Shared AgentCoordinator instance
    """
    global _coordinator_instance
    if _coordinator_instance is None:
        _coordinator_instance = AgentCoordinator()
    return _coordinator_instance