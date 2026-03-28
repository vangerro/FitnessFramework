from datetime import date
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.exercise import ExerciseOut


class WorkoutCreate(BaseModel):
    name: str
    date: date


class WorkoutOut(BaseModel):
    id: int
    name: str
    date: date

    model_config = ConfigDict(from_attributes=True)


class WorkoutDetailOut(BaseModel):
    id: int
    name: str
    date: date
    exercises: list[ExerciseOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

