from sqlalchemy import Column, ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base


class ExerciseSetTarget(Base):
    __tablename__ = "exercise_set_targets"
    __table_args__ = (UniqueConstraint("exercise_id", "set_number", name="uq_exercise_set_target"),)

    id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False, index=True)
    set_number = Column(Integer, nullable=False)
    planned_reps = Column(Integer, nullable=False)
    planned_weight = Column(Numeric(10, 2), nullable=False)

    exercise = relationship("Exercise", back_populates="targets")
