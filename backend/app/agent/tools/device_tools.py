"""
Device Control Tools for the Device Control Agent.

This module contains tool implementations for device management operations
using Strands Agents SDK.

Tools exposed to Nova Lite:
  - list_devices_tool            -> discover all devices + statuses
  - get_device_status_tool       -> inspect one specific device
  - set_device_status_tool       -> control a single device
  - update_multiple_devices_tool -> bulk-control several devices at once
"""

import logging
# from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel
from strands import tool

# from app.agent.device_data_access import get_devices, get_default_power
from app.agent.devices.backend_client import get_devices, update_device

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
# _DEFAULT_POWER = get_default_power()

logger = logging.getLogger(__name__)


# def _get_current_devices() -> list:
#     """Return the live, shared device list."""
#     return get_devices()


# ─────────────────────────────────────────────
# Pydantic schema for bulk update items
# Used so Strands generates a proper JSON schema
# that Nova Lite can fill in correctly.
# ─────────────────────────────────────────────
class DeviceUpdate(BaseModel):
    """A single device state update entry."""
    device_id: int  # numeric id of the device
    state: str      # ONLY "on" or "off"


# ─────────────────────────────────────────────
# Tools
# ─────────────────────────────────────────────

@tool
def list_devices_tool() -> Dict[str, Any]:
    """
    Return a list of ALL available devices with their current id, name, and
    status.  Call this tool FIRST whenever you need to discover what devices
    exist, resolve a device name to its id, or identify which devices are
    currently on or off before acting on them.

    Returns:
        {
          "devices": [
            {"device_id": int, "device_name": str, "status": str},
            ...
          ]
        }
    """
    logger.info("Tool Call: list_devices()")

    # current_devices = _get_current_devices()
    current_devices = get_devices()
    devices_list = [
        {
            "device_id": device["id"],
            "device_name": device["name"],
            "status": device["status"],
        }
        for device in current_devices
    ]

    observation = {"devices": devices_list}
    logger.info(f"Tool Result: {observation}")
    return observation


@tool
def get_device_status_tool(device_id: int) -> Dict[str, Any]:
    """
    Fetch the current detailed status of a single device identified by its
    numeric id.  Use this when the user asks about one specific device and
    you already know its id.

    Args:
        device_id: The numeric id of the device (e.g. 1 for Heat pump).

    Returns:
        On success: {"device_id": int, "device_name": str, "status": str}
        On failure: {"error": str, "device_id": int}
    """
    logger.info(f"Tool Call: get_device_status({device_id})")

    # current_devices = _get_current_devices()
    current_devices = get_devices()
    device = next((d for d in current_devices if d["id"] == device_id), None)

    if device is None:
        observation = {
            "error": f"Device with ID {device_id} not found",
            "device_id": device_id,
        }
    else:
        observation = {
            "device_id": device["id"],
            "device_name": device["name"],
            "status": device["status"],
        }

    logger.info(f"Tool Result: {observation}")
    return observation


@tool
def set_device_status_tool(device_id: int, state: str) -> Dict[str, Any]:
    """
    Update the state of a SINGLE device.  Prefer update_multiple_devices_tool
    when you need to control more than one device in a single step.

    Args:
        device_id: Numeric id of the target device.
        state:     New state string. ONLY "on" or "off" are valid.
                   ALL devices (including Dishwasher and Fan) use "on"/"off".

    Returns:
        {
          "success": bool,
          "message": str,
          "device_id": int,
          "old_status": str,
          "new_status": str
        }
    """
    logger.info(f"Tool Call: set_device_status({device_id}, {state})")

    # current_devices = _get_current_devices()
    current_devices = get_devices()
    device = next((d for d in current_devices if d["id"] == device_id), None)

    if device is None:
        observation = {
            "success": False,
            "message": f"Device with ID {device_id} not found",
            "device_id": device_id,
        }
    else:
        old_status = device["status"]
        # device["status"] = state
        # device["power_usage"] = (
        #     _DEFAULT_POWER.get(device["name"], 0.5) if state == "on" else 0.0
        # )
        # device["updated_at"] = datetime.now()
        
        try:
            updated_device = update_device(
                device_id=device_id,
                status=state
            )
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "device_id": device_id
            }

        observation = {
            "success": True,
            "message": f"Device '{device['name']}' (id={device_id}) updated: {old_status} -> {state}",
            "device_id": device_id,
            "old_status": old_status,
            "new_status": updated_device["status"],
        }

    logger.info(f"Tool Result: {observation}")
    return observation


@tool
def update_multiple_devices_tool(updates: List[DeviceUpdate]) -> Dict[str, Any]:
    """
    Update the state of MULTIPLE devices in a single efficient call.  Use
    this tool whenever the user's request targets two or more devices (e.g.
    "turn on Heat pump and HVAC", "turn off all devices that are on").

    Args:
        updates: A list of DeviceUpdate items. Each item must have:
                   - device_id (int) - the numeric id of the device
                   - state     (str) - ONLY "on" or "off"
                 Example:
                   [
                     {"device_id": 1, "state": "on"},
                     {"device_id": 4, "state": "on"}
                   ]

    Returns:
        {
          "results": [
            {
              "device_id": int,
              "device_name": str,
              "success": bool,
              "message": str,
              "old_status": str,
              "new_status": str
            },
            ...
          ],
          "total": int,
          "succeeded": int,
          "failed": int
        }
    """
    logger.info(f"Tool Call: update_multiple_devices({updates})")

    # current_devices = _get_current_devices()
    current_devices = get_devices()
    results = []

    for update in updates:
        # Support Pydantic model instances (normal path) and plain dicts (fallback)
        if isinstance(update, DeviceUpdate):
            device_id = update.device_id
            state = update.state
        elif isinstance(update, dict):
            device_id = update.get("device_id")
            state = update.get("state")
        else:
            results.append({
                "device_id": None,
                "success": False,
                "message": f"Unexpected update entry type: {type(update)}",
            })
            continue

        if device_id is None or state is None:
            results.append({
                "device_id": device_id,
                "success": False,
                "message": "Missing device_id or state in update entry",
            })
            continue

        device = next((d for d in current_devices if d["id"] == device_id), None)

        if device is None:
            results.append({
                "device_id": device_id,
                "success": False,
                "message": f"Device with ID {device_id} not found",
            })
        else:
            old_status = device["status"]
            # device["status"] = state
            # device["power_usage"] = (
            #     _DEFAULT_POWER.get(device["name"], 0.5) if state == "on" else 0.0
            # )
            # device["updated_at"] = datetime.now()
            
            try:
                updated_device = update_device(
                    device_id=device_id,
                    status=state
                )
            except Exception as e:
                return {
                    "success": False,
                    "message": str(e),
                    "device_id": device_id
                }

            results.append({
                "device_id": device_id,
                "device_name": device["name"],
                "success": True,
                "message": f"'{device['name']}' updated: {old_status} -> {state}",
                "old_status": old_status,
                "new_status": updated_device["status"],
            })

    succeeded = sum(1 for r in results if r.get("success"))
    observation = {
        "results": results,
        "total": len(results),
        "succeeded": succeeded,
        "failed": len(results) - succeeded,
    }

    logger.info(f"Tool Result: {observation}")
    return observation