from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.database import get_db, Chamber
from app.schemas.chamber import ChamberResponse


router = APIRouter(
    prefix="/chambers",
    tags=["Chambers"]
)


@router.get("/", response_model=list[ChamberResponse])
def get_chambers(db: Session = Depends(get_db)):
    chambers = db.query(Chamber).all()
    return chambers


@router.get("/{chamber_id}", response_model=ChamberResponse)
def get_chamber(
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

    return chamber