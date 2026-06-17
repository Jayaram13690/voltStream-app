"""
VoltStream Agents Package.

This package contains both the Device Control Agent and Energy Advisor Agent
implementations using Strands Agents SDK and Amazon Bedrock Nova 2 Lite model.

90% agentic: all decision-making is handled by Nova Lite. Python only manages
SDK initialization, tool registration, and conversation memory.
"""

from .agent_service import DeviceControlAgent, get_device_agent
from .energy_advisor_service import EnergyAdvisorAgent, get_energy_advisor
from .tools import device_tools
from .tools import energy_tools

__all__ = [
    "DeviceControlAgent", 
    "get_device_agent", 
    "EnergyAdvisorAgent",
    "get_energy_advisor",
    "device_tools",
    "energy_tools"
]