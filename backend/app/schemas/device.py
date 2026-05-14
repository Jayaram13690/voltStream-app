from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class DeviceRead(BaseModel):
    id: int
    name: str
    status: str
    power_usage: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DeviceUpdate(BaseModel):
    status: Literal["on", "off"] | None = None
