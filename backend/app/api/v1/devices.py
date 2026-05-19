from fastapi import APIRouter, HTTPException
from datetime import datetime

from app.schemas.device import DeviceRead, DeviceUpdate

router = APIRouter(prefix="/devices", tags=["devices"])

# Mock data storage
_devices = [
    {"id": 1, "name": "Heat pump", "status": "on", "power_usage": 2.1, "created_at": datetime.now(), "updated_at": datetime.now()},
    {"id": 2, "name": "EV charger", "status": "off", "power_usage": 0.0, "created_at": datetime.now(), "updated_at": datetime.now()},
    {"id": 3, "name": "Kitchen", "status": "on", "power_usage": 0.8, "created_at": datetime.now(), "updated_at": datetime.now()},
    {"id": 4, "name": "HVAC", "status": "on", "power_usage": 1.4, "created_at": datetime.now(), "updated_at": datetime.now()},
    {"id": 5, "name": "Water heater", "status": "off", "power_usage": 0.0, "created_at": datetime.now(), "updated_at": datetime.now()},
    {"id": 6, "name": "Solar inverter", "status": "on", "power_usage": 0.2, "created_at": datetime.now(), "updated_at": datetime.now()},
]

_DEFAULT_POWER: dict[str, float] = {
    "Heat pump": 2.1,
    "EV charger": 7.2,
    "Kitchen": 0.8,
    "HVAC": 1.4,
    "Water heater": 3.0,
    "Solar inverter": 0.2,
}


@router.get("", response_model=list[DeviceRead])
def list_devices() -> list[DeviceRead]:
    return [DeviceRead.model_validate(device) for device in _devices]


@router.patch("/{device_id}", response_model=DeviceRead)
def patch_device(device_id: int, body: DeviceUpdate) -> DeviceRead:
    device = next((d for d in _devices if d["id"] == device_id), None)
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    if body.status is not None:
        device["status"] = body.status
        device["power_usage"] = _DEFAULT_POWER.get(device["name"], 0.5) if body.status == "on" else 0.0
        device["updated_at"] = datetime.now()
    return DeviceRead.model_validate(device)
