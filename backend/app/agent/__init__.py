"""
Device Control Agent Package.

This package contains the Device Control Agent implementation using Strands
Agents SDK and Amazon Bedrock Nova 2 Lite model.

90 % agentic: all intent, tool-selection, and workflow decisions are made
by Nova Lite. Python only orchestrates SDK initialization and memory.
"""

from .agent_service import DeviceControlAgent, get_device_agent
from .tools import device_tools

__all__ = ["DeviceControlAgent", "get_device_agent", "device_tools"]