from pydantic import BaseModel


class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    category: str
    volume_cbm: float

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    sku: str
    name: str
    category: str
    volume_cbm: float


class ProductUpdate(BaseModel):
    sku: str | None = None
    name: str | None = None
    category: str | None = None
    volume_cbm: float | None = None