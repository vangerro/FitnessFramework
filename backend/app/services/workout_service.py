from sqlalchemy.orm import Session, selectinload

from app.models.exercise import Exercise
from app.models.exercise_set_log import ExerciseSetLog
from app.models.workout import Workout
from app.models.workout_plan import WorkoutPlan
from app.models.workout_session import WorkoutSession


def create_workout(
    db: Session,
    *,
    user_id: int,
    name: str,
    date,
    plan_id: int | None = None,
    day_number: int | None = None,
) -> Workout:
    workout = Workout(
        user_id=user_id,
        name=name,
        date=date,
        plan_id=plan_id,
        day_number=day_number,
    )
    db.add(workout)
    db.commit()
    db.refresh(workout)
    return workout


def create_workout_plan(db: Session, *, user_id: int, name: str) -> WorkoutPlan:
    plan = WorkoutPlan(user_id=user_id, name=name)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def list_workouts(db: Session, *, user_id: int) -> list[Workout]:
    return (
        db.query(Workout)
        .filter(Workout.user_id == user_id)
        .order_by(Workout.date.asc(), Workout.id.asc())
        .all()
    )


def list_workout_plans(db: Session, *, user_id: int) -> list[WorkoutPlan]:
    return (
        db.query(WorkoutPlan)
        .options(selectinload(WorkoutPlan.workouts))
        .filter(WorkoutPlan.user_id == user_id)
        .order_by(WorkoutPlan.created_at.desc(), WorkoutPlan.id.desc())
        .all()
    )


def get_workout_plan_with_details(
    db: Session, *, user_id: int, plan_id: int
) -> WorkoutPlan | None:
    return (
        db.query(WorkoutPlan)
        .options(
            selectinload(WorkoutPlan.workouts).selectinload(Workout.exercises),
            selectinload(WorkoutPlan.workouts)
            .selectinload(Workout.sessions)
            .selectinload(WorkoutSession.set_logs),
        )
        .filter(WorkoutPlan.user_id == user_id, WorkoutPlan.id == plan_id)
        .first()
    )


def rename_workout_plan(
    db: Session, *, user_id: int, plan_id: int, name: str
) -> WorkoutPlan | None:
    plan = (
        db.query(WorkoutPlan)
        .filter(WorkoutPlan.user_id == user_id, WorkoutPlan.id == plan_id)
        .first()
    )
    if not plan:
        return None
    plan.name = name
    db.commit()
    db.refresh(plan)
    return plan


def delete_workout_plan(db: Session, *, user_id: int, plan_id: int) -> bool:
    plan = (
        db.query(WorkoutPlan)
        .filter(WorkoutPlan.user_id == user_id, WorkoutPlan.id == plan_id)
        .first()
    )
    if not plan:
        return False
    db.delete(plan)
    db.commit()
    return True


def list_recent_sessions_for_plan(
    db: Session, *, user_id: int, plan_id: int, limit: int = 20
) -> list[WorkoutSession]:
    return (
        db.query(WorkoutSession)
        .join(Workout, Workout.id == WorkoutSession.workout_id)
        .options(selectinload(WorkoutSession.set_logs))
        .filter(
            WorkoutSession.user_id == user_id,
            Workout.plan_id == plan_id,
        )
        .order_by(WorkoutSession.performed_at.desc(), WorkoutSession.id.desc())
        .limit(limit)
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


def create_workout_session_with_set_logs(
    db: Session,
    *,
    user_id: int,
    plan_id: int,
    workout_id: int,
    set_logs: list[dict],
) -> WorkoutSession | None:
    workout = (
        db.query(Workout)
        .options(selectinload(Workout.exercises))
        .filter(
            Workout.user_id == user_id,
            Workout.id == workout_id,
            Workout.plan_id == plan_id,
        )
        .first()
    )
    if not workout:
        return None

    exercise_ids = {exercise.id for exercise in workout.exercises}
    if not set_logs:
        return None
    if any(log["exercise_id"] not in exercise_ids for log in set_logs):
        return None

    session = WorkoutSession(workout_id=workout_id, user_id=user_id)
    db.add(session)
    db.flush()

    for log in set_logs:
        db.add(
            ExerciseSetLog(
                session_id=session.id,
                exercise_id=log["exercise_id"],
                set_number=log["set_number"],
                reps=log["reps"],
                weight=log["weight"],
            )
        )

    db.commit()
    return (
        db.query(WorkoutSession)
        .options(selectinload(WorkoutSession.set_logs))
        .filter(WorkoutSession.id == session.id)
        .first()
    )

