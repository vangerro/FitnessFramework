from datetime import date, timedelta
from decimal import Decimal
import re

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.plan import GeneratedPlan, PlanGenerateRequest, SavePlanRequest
from app.schemas.exercise import ExerciseCreate, ExerciseOut
from app.schemas.workout import WorkoutCreate, WorkoutDetailOut, WorkoutOut
from app.services.plan_generator import build_generated_plan
from app.services.workout_service import (
    add_exercise,
    create_workout,
    delete_workout,
    get_workout_with_exercises,
    list_workouts,
)

router = APIRouter()


@router.post("/generate", response_model=GeneratedPlan)
def generate_workout_plan(
    payload: PlanGenerateRequest,
    current_user=Depends(get_current_user),
):
    # Auth dependency keeps this endpoint private to logged in users.
    # The generated plan is deterministic in shape but randomized in exercise ordering.
    _ = current_user
    return build_generated_plan(
        days=payload.days,
        focus=payload.focus,
        periodization=payload.periodization,
        experience_level=payload.experience_level,
        start_date=payload.start_date,
    )


@router.post("/save-plan")
def save_generated_plan(
    payload: SavePlanRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not payload.days:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plan must include at least one workout day",
        )

    created_workout_ids: list[int] = []
    fallback_start_date = payload.days[0].date or date.today()

    for index, day in enumerate(payload.days):
        workout_date = day.date or (fallback_start_date + timedelta(days=index))
        workout = create_workout(
            db,
            user_id=current_user.id,
            name=day.name,
            date=workout_date,
        )
        created_workout_ids.append(workout.id)

        for exercise in day.exercises:
            reps_for_storage = exercise.reps or _reps_from_ranges(exercise.rep_ranges)
            name = exercise.name
            if exercise.is_progression and exercise.rep_ranges:
                name = f"{name} (RPP: {' / '.join(exercise.rep_ranges)})"
            add_exercise(
                db,
                user_id=current_user.id,
                workout_id=workout.id,
                name=name,
                sets=exercise.sets,
                reps=reps_for_storage,
                weight=Decimal("0"),
            )

    return {"created_workout_ids": created_workout_ids}


@router.post("", response_model=WorkoutOut)
def create_new_workout(
    payload: WorkoutCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workout = create_workout(db, user_id=current_user.id, name=payload.name, date=payload.date)
    return workout


@router.get("", response_model=list[WorkoutOut])
def get_my_workouts(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_workouts(db, user_id=current_user.id)


@router.get("/{workout_id}", response_model=WorkoutDetailOut)
def get_workout_detail(
    workout_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workout = get_workout_with_exercises(
        db, user_id=current_user.id, workout_id=workout_id
    )
    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found")
    return workout


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_workout(
    workout_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ok = delete_workout(db, user_id=current_user.id, workout_id=workout_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{workout_id}/exercises", response_model=ExerciseOut)
def add_workout_exercise(
    workout_id: int,
    payload: ExerciseCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exercise = add_exercise(
        db,
        user_id=current_user.id,
        workout_id=workout_id,
        name=payload.name,
        sets=payload.sets,
        reps=payload.reps,
        weight=payload.weight,
    )
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found"
        )
    return exercise


def _reps_from_ranges(rep_ranges: list[str]) -> int:
    if not rep_ranges:
        return 1
    first_range = rep_ranges[0]
    match = re.search(r"(\d+)", first_range)
    if not match:
        return 1
    return int(match.group(1))

