from __future__ import annotations

from datetime import date as DateType
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.data.exercise_catalog import BALANCED_KEYWORD, BODY_PARTS

Periodization = Literal["strength", "hypertrophy"]
ExperienceLevel = Literal["beginner", "intermediate", "advanced"]
DayRole = Literal[
    "full_body",
    "upper",
    "lower",
    "push",
    "pull",
    "legs",
    "aesthetic",
    "cardio",
]
FocusBodyPart = Literal[
    "chest",
    "quads",
    "hamstrings",
    "bis",
    "tris",
    "shoulder",
    "back",
    "cardio",
]
FocusValue = Literal[
    "balanced",
    "chest",
    "quads",
    "hamstrings",
    "bis",
    "tris",
    "shoulder",
    "back",
]


class PlanGenerateRequest(BaseModel):
    days: int = Field(ge=1, le=5)
    focus: list[FocusValue]
    periodization: Periodization
    experience_level: ExperienceLevel
    start_date: DateType | None = None

    @model_validator(mode="after")
    def validate_focus(self) -> "PlanGenerateRequest":
        if not self.focus:
            raise ValueError("At least one focus value is required")

        if BALANCED_KEYWORD in self.focus and len(self.focus) > 1:
            raise ValueError("'balanced' cannot be combined with other focus values")

        allowed = set(BODY_PARTS) | {BALANCED_KEYWORD}
        invalid = [value for value in self.focus if value not in allowed]
        if invalid:
            raise ValueError(f"Invalid focus value(s): {', '.join(invalid)}")

        return self


class GeneratedExercise(BaseModel):
    name: str
    sets: int = Field(ge=1)
    reps: int | None = Field(default=None, ge=1)
    rep_ranges: list[str] = Field(default_factory=list)
    body_part: FocusBodyPart
    level: ExperienceLevel
    tags: list[str] = Field(default_factory=list)
    is_progression: bool = False


class GeneratedWorkoutDay(BaseModel):
    day_number: int = Field(ge=1)
    name: str
    day_role: DayRole
    date: DateType | None = None
    exercises: list[GeneratedExercise] = Field(default_factory=list)


class GeneratedPlan(BaseModel):
    days: list[GeneratedWorkoutDay] = Field(default_factory=list)


class SavePlanRequest(BaseModel):
    name: str = Field(min_length=1)
    days: list[GeneratedWorkoutDay] = Field(default_factory=list)
