from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.base import Base


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    performed_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    workout = relationship("Workout", back_populates="sessions")
    set_logs = relationship(
        "ExerciseSetLog",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
