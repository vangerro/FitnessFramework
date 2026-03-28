from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.exercise import ExerciseCreate, ExerciseOut
from app.schemas.workout import WorkoutCreate, WorkoutDetailOut, WorkoutOut
from app.services.workout_service import (
    add_exercise,
    create_workout,
    delete_workout,
    get_workout_with_exercises,
    list_workouts,
)

router = APIRouter()


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

