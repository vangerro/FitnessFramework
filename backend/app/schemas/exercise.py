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
    targets: list["ExerciseSetTargetOut"] = Field(default_factory=list)

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


class ExerciseSetTargetUpdate(BaseModel):
    set_number: int = Field(ge=1)
    planned_reps: int = Field(ge=1)
    planned_weight: Decimal = Field(ge=0)


class ExerciseSetTargetOut(BaseModel):
    id: int
    exercise_id: int
    set_number: int
    planned_reps: int
    planned_weight: Decimal

    model_config = ConfigDict(from_attributes=True)

