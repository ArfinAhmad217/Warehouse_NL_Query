from pydantic import BaseModel
from datetime import datetime


class CapacityLogResponse(BaseModel):
    id: int
    chamber_id: int
    log_date: datetime
    used_capacity_cbm: float
    total_capacity_cbm: float
    utilization_pct: float

    class Config:
        from_attributes = True


class ChamberUtilizationResponse(BaseModel):
    chamber_id: int
    chamber_name: str
    average_utilization_pct: float
    maximum_utilization_pct: float
    minimum_utilization_pct: float


class WarehouseUtilizationResponse(BaseModel):
    total_capacity_cbm: float
    average_used_capacity_cbm: float
    average_utilization_pct: float