"""
Device Control Tools for the Device Control Agent.

This module contains the tool implementations for device management operations
using Strands Agents SDK.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from strands import tool
from app.services.device_data_access import get_devices, get_default_power

# Get device data access functions (don't store local copies)
_DEFAULT_POWER = get_default_power()

# Helper function to get fresh device data each time
def _get_current_devices():
    return get_devices()

# Configure logging
logger = logging.getLogger(__name__)


@tool
def list_devices_tool() -> List[Dict[str, Any]]:
    """List all available devices"""
    logger.info("Tool Call: list_devices()")
    
    # Get fresh device data
    current_devices = _get_current_devices()
    
    devices_list = [
        {
            "device_id": device["id"],
            "device_name": device["name"],
            "status": device["status"]
        }
        for device in current_devices
    ]
    
    observation = {"devices": devices_list}
    logger.info(f"Tool Result: {observation}")
    
    return observation


@tool
def get_device_status_tool(device_id: int) -> Dict[str, Any]:
    """Get status of a specific device"""
    logger.info(f"Tool Call: get_device_status({device_id})")
    
    # Get fresh device data
    current_devices = _get_current_devices()
    device = next((d for d in current_devices if d["id"] == device_id), None)
    
    if device is None:
        observation = {
            "error": f"Device with ID {device_id} not found",
            "device_id": device_id
        }
    else:
        observation = {
            "device_id": device["id"],
            "device_name": device["name"],
            "status": device["status"]
        }
    
    logger.info(f"Tool Result: {observation}")
    return observation


@tool
def set_device_status_tool(device_id: int, state: str) -> Dict[str, Any]:
    """Set status of a specific device"""
    logger.info(f"Tool Call: set_device_status({device_id}, {state})")
    
    # Get fresh device data
    current_devices = _get_current_devices()
    device = next((d for d in current_devices if d["id"] == device_id), None)
    
    if device is None:
        observation = {
            "success": False,
            "message": f"Device with ID {device_id} not found",
            "device_id": device_id
        }
    else:
        # Update device status
        old_status = device["status"]
        device["status"] = state
        device["power_usage"] = _DEFAULT_POWER.get(device["name"], 0.5) if state in ["on", "online"] else 0.0
        device["updated_at"] = datetime.now()
        
        observation = {
            "success": True,
            "message": f"Device {device_id} status updated from {old_status} to {state}",
            "device_id": device_id,
            "old_status": old_status,
            "new_status": state
        }
    
    logger.info(f"Tool Result: {observation}")
    return observation