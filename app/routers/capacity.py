from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db, CapacityLog, Chamber
from app.schemas.capacity import (
    CapacityLogResponse,
    ChamberUtilizationResponse,
    WarehouseUtilizationResponse
)


router = APIRouter(
    prefix="/capacity",
    tags=["Capacity Analytics"]
)


# =========================================================
# GET ALL CAPACITY LOGS
# =========================================================

@router.get(
    "/logs",
    response_model=list[CapacityLogResponse]
)
def get_capacity_logs(
    db: Session = Depends(get_db)
):
    logs = (
        db.query(CapacityLog)
        .order_by(CapacityLog.log_date.desc())
        .all()
    )

    return logs


# =========================================================
# GET CAPACITY LOGS FOR A CHAMBER
# =========================================================

@router.get(
    "/chamber/{chamber_id}",
    response_model=list[CapacityLogResponse]
)
def get_chamber_capacity(
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

    logs = (
        db.query(CapacityLog)
        .filter(CapacityLog.chamber_id == chamber_id)
        .order_by(CapacityLog.log_date.desc())
        .all()
    )

    return logs


# =========================================================
# CHAMBER UTILIZATION SUMMARY
# =========================================================

@router.get(
    "/chamber/{chamber_id}/summary",
    response_model=ChamberUtilizationResponse
)
def get_chamber_utilization(
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

    result = (
        db.query(
            func.avg(CapacityLog.utilization_pct),
            func.max(CapacityLog.utilization_pct),
            func.min(CapacityLog.utilization_pct)
        )
        .filter(CapacityLog.chamber_id == chamber_id)
        .first()
    )

    return {
        "chamber_id": chamber.id,
        "chamber_name": chamber.name,
        "average_utilization_pct": round(result[0] or 0, 2),
        "maximum_utilization_pct": round(result[1] or 0, 2),
        "minimum_utilization_pct": round(result[2] or 0, 2)
    }


# =========================================================
# WAREHOUSE UTILIZATION SUMMARY
# =========================================================

@router.get(
    "/summary",
    response_model=WarehouseUtilizationResponse
)
def get_warehouse_summary(
    db: Session = Depends(get_db)
):

    result = (
        db.query(
            func.sum(CapacityLog.total_capacity_cbm),
            func.avg(CapacityLog.used_capacity_cbm),
            func.avg(CapacityLog.utilization_pct)
        )
        .first()
    )

    return {
        "total_capacity_cbm": round(result[0] or 0, 2),
        "average_used_capacity_cbm": round(result[1] or 0, 2),
        "average_utilization_pct": round(result[2] or 0, 2)
    }


# =========================================================
# MOST UTILIZED CHAMBER
# =========================================================

@router.get("/most-utilized")
def get_most_utilized_chamber(
    db: Session = Depends(get_db)
):

    result = (
        db.query(
            Chamber.id,
            Chamber.name,
            func.avg(CapacityLog.utilization_pct).label(
                "average_utilization_pct"
            )
        )
        .join(
            CapacityLog,
            CapacityLog.chamber_id == Chamber.id
        )
        .group_by(
            Chamber.id,
            Chamber.name
        )
        .order_by(
            func.avg(CapacityLog.utilization_pct).desc()
        )
        .first()
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="No capacity data found"
        )

    return {
        "chamber_id": result.id,
        "chamber_name": result.name,
        "average_utilization_pct": round(
            result.average_utilization_pct,
            2
        )
    }


# =========================================================
# LEAST UTILIZED CHAMBER
# =========================================================

@router.get("/least-utilized")
def get_least_utilized_chamber(
    db: Session = Depends(get_db)
):

    result = (
        db.query(
            Chamber.id,
            Chamber.name,
            func.avg(CapacityLog.utilization_pct).label(
                "average_utilization_pct"
            )
        )
        .join(
            CapacityLog,
            CapacityLog.chamber_id == Chamber.id
        )
        .group_by(
            Chamber.id,
            Chamber.name
        )
        .order_by(
            func.avg(CapacityLog.utilization_pct).asc()
        )
        .first()
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="No capacity data found"
        )

    return {
        "chamber_id": result.id,
        "chamber_name": result.name,
        "average_utilization_pct": round(
            result.average_utilization_pct,
            2
        )
    }