from sqlalchemy import Column, ForeignKey, Integer, Numeric
from sqlalchemy.orm import relationship

from app.db.base import Base


class ExerciseSetLog(Base):
    __tablename__ = "exercise_set_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        Integer, ForeignKey("workout_sessions.id"), nullable=False, index=True
    )
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False, index=True)
    set_number = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    weight = Column(Numeric(10, 2), nullable=False)

    session = relationship("WorkoutSession", back_populates="set_logs")
    exercise = relationship("Exercise", back_populates="set_logs")
