"""
Device Data Access Module.

This module provides access to the shared device data without creating circular imports.
"""

from datetime import datetime

# Initialize device data with proper timestamps
import copy

# Original device data template
_DEVICE_TEMPLATE = [
    {"id": 1, "name": "Heat pump", "status": "on", "power_usage": 2.1},
    {"id": 2, "name": "EV charger", "status": "off", "power_usage": 0.0},
    {"id": 3, "name": "Kitchen", "status": "on", "power_usage": 0.8},
    {"id": 4, "name": "HVAC", "status": "on", "power_usage": 1.4},
    {"id": 5, "name": "Water heater", "status": "off", "power_usage": 0.0},
    {"id": 6, "name": "Solar inverter", "status": "on", "power_usage": 0.2},
    {"id": 101, "name": "Dishwasher", "status": "online", "power_usage": 1.5},
    {"id": 102, "name": "Fan", "status": "offline", "power_usage": 0.0},
]

# Initialize devices with proper timestamps
_devices = [
    {**device, "created_at": datetime.now(), "updated_at": datetime.now()}
    for device in _DEVICE_TEMPLATE
]

_DEFAULT_POWER: dict[str, float] = {
    "Heat pump": 2.1,
    "EV charger": 7.2,
    "Kitchen": 0.8,
    "HVAC": 1.4,
    "Water heater": 3.0,
    "Solar inverter": 0.2,
    "Dishwasher": 1.5,
    "Fan": 0.3,
}


def get_devices():
    """Get the shared devices list"""
    return _devices


def get_default_power():
    """Get the default power mapping"""
    return _DEFAULT_POWER


def reset_devices():
    """Reset all devices to their initial state"""
    global _devices
    _devices = [
        {**device, "created_at": datetime.now(), "updated_at": datetime.now()}
        for device in _DEVICE_TEMPLATE
    ]