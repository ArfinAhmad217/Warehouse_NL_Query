from pydantic import BaseModel


class ChamberResponse(BaseModel):
    id: int
    name: str
    location: str
    total_capacity_cbm: float
    is_active: bool

    class Config:
        from_attributes = True