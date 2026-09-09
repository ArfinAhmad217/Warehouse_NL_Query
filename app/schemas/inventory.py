from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class InventoryResponse(BaseModel):
    id: int
    chamber_id: int
    product_id: int
    quantity: int
    snapshot_date: datetime
    used_capacity_cbm: float

    class Config:
        from_attributes = True


class InventoryCreate(BaseModel):
    chamber_id: int
    product_id: int
    quantity: int
    snapshot_date: datetime
    used_capacity_cbm: float


class InventoryUpdate(BaseModel):
    chamber_id: Optional[int] = None
    product_id: Optional[int] = None
    quantity: Optional[int] = None
    snapshot_date: Optional[datetime] = None
    used_capacity_cbm: Optional[float] = None