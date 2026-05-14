from pydantic import BaseModel, Field


class DashboardLive(BaseModel):
    grid_usage: float = Field(..., description="kW drawn from grid")
    solar_generation: float = Field(..., description="kW from solar")
    battery: int = Field(..., ge=0, le=100, description="Battery state of charge %")
    savings: float = Field(..., description="Month-to-date savings (currency units)")
