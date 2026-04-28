from sqlalchemy import Column, Integer, ForeignKey, String, Numeric
from sqlalchemy.orm import relationship

from app.db.base import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False, index=True)

    name = Column(String, nullable=False)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    weight = Column(Numeric(10, 2), nullable=False)

    workout = relationship("Workout", back_populates="exercises")
    set_logs = relationship(
        "ExerciseSetLog",
        back_populates="exercise",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

