import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.db.base import Base
from app.core.database import get_db

# Ensure all ORM models are imported so Base.metadata includes their tables.
from app.models.user import User  # noqa: F401
from app.models.workout import Workout  # noqa: F401
from app.models.exercise import Exercise  # noqa: F401
from app.models.workout_plan import WorkoutPlan  # noqa: F401
from app.models.workout_session import WorkoutSession  # noqa: F401
from app.models.exercise_set_log import ExerciseSetLog  # noqa: F401
from app.models.exercise_set_target import ExerciseSetTarget  # noqa: F401
from app.models.weight import Weight  # noqa: F401
from app.models.body_measurement import BodyMeasurement  # noqa: F401

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
