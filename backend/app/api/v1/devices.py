from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.device import Device
from app.schemas.device import DeviceRead, DeviceUpdate

router = APIRouter(prefix="/devices", tags=["devices"])

_DEFAULT_POWER: dict[str, float] = {
    "Heat pump": 2.1,
    "EV charger": 7.2,
    "Kitchen": 0.8,
    "HVAC": 1.4,
    "Water heater": 3.0,
    "Solar inverter": 0.2,
}


@router.get("", response_model=list[DeviceRead])
def list_devices(db: Session = Depends(get_db)) -> list[Device]:
    return db.query(Device).order_by(Device.id).all()


@router.patch("/{device_id}", response_model=DeviceRead)
def patch_device(device_id: int, body: DeviceUpdate, db: Session = Depends(get_db)) -> Device:
    device = db.get(Device, device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    if body.status is not None:
        device.status = body.status
        if body.status == "on":
            device.power_usage = _DEFAULT_POWER.get(device.name, 0.5)
        else:
            device.power_usage = 0.0
    db.add(device)
    db.commit()
    db.refresh(device)
    return device
