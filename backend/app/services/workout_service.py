from sqlalchemy.orm import Session, selectinload

from app.models.exercise import Exercise
from app.models.workout import Workout


def create_workout(db: Session, *, user_id: int, name: str, date) -> Workout:
    workout = Workout(user_id=user_id, name=name, date=date)
    db.add(workout)
    db.commit()
    db.refresh(workout)
    return workout


def list_workouts(db: Session, *, user_id: int) -> list[Workout]:
    return (
        db.query(Workout)
        .filter(Workout.user_id == user_id)
        .order_by(Workout.date.asc(), Workout.id.asc())
        .all()
    )


def delete_workout(db: Session, *, user_id: int, workout_id: int) -> bool:
    workout = db.query(Workout).filter(Workout.user_id == user_id, Workout.id == workout_id).first()
    if not workout:
        return False
    db.delete(workout)
    db.commit()
    return True


def get_workout_with_exercises(
    db: Session, *, user_id: int, workout_id: int
) -> Workout | None:
    return (
        db.query(Workout)
        .options(selectinload(Workout.exercises))
        .filter(Workout.user_id == user_id, Workout.id == workout_id)
        .first()
    )


def add_exercise(
    db: Session,
    *,
    user_id: int,
    workout_id: int,
    name: str,
    sets: int,
    reps: int,
    weight,
) -> Exercise | None:
    workout = db.query(Workout).filter(Workout.user_id == user_id, Workout.id == workout_id).first()
    if not workout:
        return None

    exercise = Exercise(
        workout_id=workout_id,
        name=name,
        sets=sets,
        reps=reps,
        weight=weight,
    )
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise

