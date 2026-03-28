from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ExerciseCreate(BaseModel):
    name: str
    sets: int
    reps: int
    weight: Decimal


class ExerciseOut(BaseModel):
    id: int
    name: str
    sets: int
    reps: int
    weight: Decimal

    model_config = ConfigDict(from_attributes=True)

