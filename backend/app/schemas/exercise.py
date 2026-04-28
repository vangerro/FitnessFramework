from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


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


class ExerciseSetLogCreate(BaseModel):
    exercise_id: int
    set_number: int = Field(ge=1)
    reps: int = Field(ge=1)
    weight: Decimal = Field(ge=0)


class ExerciseSetLogOut(BaseModel):
    id: int
    session_id: int
    exercise_id: int
    set_number: int
    reps: int
    weight: Decimal

    model_config = ConfigDict(from_attributes=True)

