from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.exercise import ExerciseOut, ExerciseSetLogCreate, ExerciseSetLogOut


class WorkoutCreate(BaseModel):
    name: str
    date: date


class WorkoutOut(BaseModel):
    id: int
    name: str
    date: date
    plan_id: int | None = None
    day_number: int | None = None

    model_config = ConfigDict(from_attributes=True)


class WorkoutDetailOut(BaseModel):
    id: int
    name: str
    date: date
    exercises: list[ExerciseOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class WorkoutPlanOut(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime
    workout_count: int = Field(ge=0)

    model_config = ConfigDict(from_attributes=True)


class WorkoutPlanDetailOut(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime
    workouts: list[WorkoutDetailOut] = Field(default_factory=list)
    recent_sessions: list["WorkoutSessionOut"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class WorkoutPlanRenameRequest(BaseModel):
    name: str = Field(min_length=1)


class WorkoutSessionCreateRequest(BaseModel):
    set_logs: list[ExerciseSetLogCreate] = Field(default_factory=list)


class WorkoutSessionOut(BaseModel):
    id: int
    workout_id: int
    user_id: int
    performed_at: datetime
    set_logs: list[ExerciseSetLogOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

