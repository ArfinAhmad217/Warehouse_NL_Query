from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import (
    get_db,
    InventorySnapshot,
    Chamber,
    Product
)

from app.schemas.inventory import (
    InventoryResponse,
    InventoryCreate,
    InventoryUpdate
)


router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"]
)


# GET ALL INVENTORY
@router.get("/", response_model=list[InventoryResponse])
def get_inventory(
    db: Session = Depends(get_db)
):
    inventory = db.query(InventorySnapshot).all()
    return inventory


# GET INVENTORY BY ID
@router.get("/{inventory_id}", response_model=InventoryResponse)
def get_inventory_by_id(
    inventory_id: int,
    db: Session = Depends(get_db)
):
    inventory = (
        db.query(InventorySnapshot)
        .filter(InventorySnapshot.id == inventory_id)
        .first()
    )

    if not inventory:
        raise HTTPException(
            status_code=404,
            detail="Inventory record not found"
        )

    return inventory


# GET INVENTORY BY CHAMBER
@router.get("/chamber/{chamber_id}", response_model=list[InventoryResponse])
def get_inventory_by_chamber(
    chamber_id: int,
    db: Session = Depends(get_db)
):
    chamber = (
        db.query(Chamber)
        .filter(Chamber.id == chamber_id)
        .first()
    )

    if not chamber:
        raise HTTPException(
            status_code=404,
            detail="Chamber not found"
        )

    inventory = (
        db.query(InventorySnapshot)
        .filter(InventorySnapshot.chamber_id == chamber_id)
        .all()
    )

    return inventory


# GET INVENTORY BY PRODUCT
@router.get("/product/{product_id}", response_model=list[InventoryResponse])
def get_inventory_by_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    inventory = (
        db.query(InventorySnapshot)
        .filter(InventorySnapshot.product_id == product_id)
        .all()
    )

    return inventory


# CREATE INVENTORY
@router.post("/", response_model=InventoryResponse, status_code=201)
def create_inventory(
    inventory_data: InventoryCreate,
    db: Session = Depends(get_db)
):
    # Check chamber
    chamber = (
        db.query(Chamber)
        .filter(Chamber.id == inventory_data.chamber_id)
        .first()
    )

    if not chamber:
        raise HTTPException(
            status_code=404,
            detail="Chamber not found"
        )

    # Check product
    product = (
        db.query(Product)
        .filter(Product.id == inventory_data.product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    inventory = InventorySnapshot(
        chamber_id=inventory_data.chamber_id,
        product_id=inventory_data.product_id,
        quantity=inventory_data.quantity,
        snapshot_date=inventory_data.snapshot_date,
        used_capacity_cbm=inventory_data.used_capacity_cbm
    )

    db.add(inventory)
    db.commit()
    db.refresh(inventory)

    return inventory


# UPDATE INVENTORY
@router.put("/{inventory_id}", response_model=InventoryResponse)
def update_inventory(
    inventory_id: int,
    inventory_data: InventoryUpdate,
    db: Session = Depends(get_db)
):
    inventory = (
        db.query(InventorySnapshot)
        .filter(InventorySnapshot.id == inventory_id)
        .first()
    )

    if not inventory:
        raise HTTPException(
            status_code=404,
            detail="Inventory record not found"
        )

    update_data = inventory_data.model_dump(
        exclude_unset=True
    )

    # Validate chamber if being updated
    if "chamber_id" in update_data:
        chamber = (
            db.query(Chamber)
            .filter(Chamber.id == update_data["chamber_id"])
            .first()
        )

        if not chamber:
            raise HTTPException(
                status_code=404,
                detail="Chamber not found"
            )

    # Validate product if being updated
    if "product_id" in update_data:
        product = (
            db.query(Product)
            .filter(Product.id == update_data["product_id"])
            .first()
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

    for key, value in update_data.items():
        setattr(inventory, key, value)

    db.commit()
    db.refresh(inventory)

    return inventory


# DELETE INVENTORY
@router.delete("/{inventory_id}")
def delete_inventory(
    inventory_id: int,
    db: Session = Depends(get_db)
):
    inventory = (
        db.query(InventorySnapshot)
        .filter(InventorySnapshot.id == inventory_id)
        .first()
    )

    if not inventory:
        raise HTTPException(
            status_code=404,
            detail="Inventory record not found"
        )

    db.delete(inventory)
    db.commit()

    return {
        "message": "Inventory record deleted successfully"
    }