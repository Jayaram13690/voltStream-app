"""
Device Control Tools Package.

This package contains all tool implementations for the Device Control Agent.
"""

from .device_tools import (
    list_devices_tool,
    get_device_status_tool,
    set_device_status_tool,
    update_multiple_devices_tool,
)

__all__ = [
    "list_devices_tool",
    "get_device_status_tool",
    "set_device_status_tool",
    "update_multiple_devices_tool",
]

# Tool registry for easy access
device_tools = {
    "list_devices": list_devices_tool,
    "get_device_status": get_device_status_tool,
    "set_device_status": set_device_status_tool,
    "update_multiple_devices": update_multiple_devices_tool,
}