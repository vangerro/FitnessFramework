from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.weight import Weight
from app.schemas.weight import WeightCreate, WeightOut

router = APIRouter()


@router.post("", response_model=WeightOut)
def add_weight(
    payload: WeightCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entry = Weight(
        user_id=current_user.id,
        weight=payload.weight,
        date=payload.date,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("", response_model=list[WeightOut])
def list_weights(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(Weight)
        .filter(Weight.user_id == current_user.id)
        .order_by(Weight.date.asc(), Weight.id.asc())
        .all()
    )
