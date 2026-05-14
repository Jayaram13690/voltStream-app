from typing import Literal

from pydantic import BaseModel


class AnalyticsPoint(BaseModel):
    label: str
    consumption: float
    solar: float


class AnalyticsHistory(BaseModel):
    period: Literal["daily", "weekly", "monthly"]
    points: list[AnalyticsPoint]
