from fastapi import APIRouter, HTTPException
from datetime import datetime

from app.schemas.device import DeviceRead, DeviceUpdate

router = APIRouter(prefix="/devices", tags=["devices"])

# Import shared device data
from app.api.v1.device_data_access import get_devices, get_default_power

# Get shared device data
_devices = get_devices()
_DEFAULT_POWER = get_default_power()


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
