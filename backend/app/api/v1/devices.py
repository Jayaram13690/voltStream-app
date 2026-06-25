from fastapi import APIRouter, HTTPException
from datetime import datetime

from app.schemas.device import DeviceRead, DeviceUpdate

router = APIRouter(prefix="/devices", tags=["devices"])

# Import S3 device service
from app.services.s3_device_service import S3DeviceService

# Initialize S3 device service
device_service = S3DeviceService()


@router.get("", response_model=list[DeviceRead])
def list_devices() -> list[DeviceRead]:
    try:
        devices = device_service.get_devices()
        return [DeviceRead.model_validate(device) for device in devices]
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{device_id}", response_model=DeviceRead)
def patch_device(device_id: int, body: DeviceUpdate) -> DeviceRead:
    try:
        if body.status is not None:
            device = device_service.update_device(device_id, body.status)
            return DeviceRead.model_validate(device)
        else:
            # If no status provided, just return current device
            device = device_service.get_device(device_id)
            if device is None:
                raise HTTPException(status_code=404, detail="Device not found")
            return DeviceRead.model_validate(device)
    except RuntimeError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail="Device not found")
        else:
            raise HTTPException(status_code=500, detail=str(e))
