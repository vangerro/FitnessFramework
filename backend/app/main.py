import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import inspect, text

from app.core.database import engine
from app.db.base import Base
from app.routers import auth, users, weight, body_measurement, workouts


def _import_models() -> None:
    # Register all ORM tables on Base.metadata before create_all().
    import app.models.body_measurement  # noqa: F401
    import app.models.exercise  # noqa: F401
    import app.models.exercise_set_log  # noqa: F401
    import app.models.user  # noqa: F401
    import app.models.weight  # noqa: F401
    import app.models.workout  # noqa: F401
    import app.models.workout_plan  # noqa: F401
    import app.models.workout_session  # noqa: F401


def _ensure_workout_tracking_schema() -> None:
    """Create new workout-tracking tables and backfill required workout columns."""
    _import_models()
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    if "workouts" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("workouts")}
    statements: list[str] = []
    if "plan_id" not in existing_columns:
        statements.append("ALTER TABLE workouts ADD COLUMN plan_id INTEGER")
    if "day_number" not in existing_columns:
        statements.append("ALTER TABLE workouts ADD COLUMN day_number INTEGER")

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


@asynccontextmanager
async def lifespan(app: FastAPI):
    _ensure_workout_tracking_schema()
    if os.getenv("AUTO_CREATE_SCHEMA", "").lower() in ("1", "true", "yes"):
        _import_models()
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="FitnessFramework API", lifespan=lifespan)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(weight.router, prefix="/weight", tags=["weight"])
app.include_router(body_measurement.router, prefix="/measurements", tags=["body_measurements"])
app.include_router(workouts.router, prefix="/workouts", tags=["workouts"])

@app.get("/health")
def health():
    return {"status": "ok"}
