from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class BodyMeasurementCreate(BaseModel):
    chest: Decimal
    waist: Decimal
    arms: Decimal
    date: date


class BodyMeasurementOut(BaseModel):
    id: int
    chest: Decimal
    waist: Decimal
    arms: Decimal
    date: date

    model_config = ConfigDict(from_attributes=True)

