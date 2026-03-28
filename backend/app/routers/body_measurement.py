from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.body_measurement import BodyMeasurement
from app.schemas.body_measurement import BodyMeasurementCreate, BodyMeasurementOut

router = APIRouter()


@router.post("", response_model=BodyMeasurementOut)
def add_measurement(
    payload: BodyMeasurementCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    measurement = BodyMeasurement(
        user_id=current_user.id,
        chest=payload.chest,
        waist=payload.waist,
        arms=payload.arms,
        date=payload.date,
    )
    db.add(measurement)
    db.commit()
    db.refresh(measurement)
    return measurement


@router.get("", response_model=list[BodyMeasurementOut])
def list_measurements(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(BodyMeasurement)
        .filter(BodyMeasurement.user_id == current_user.id)
        .order_by(BodyMeasurement.date.asc(), BodyMeasurement.id.asc())
        .all()
    )
