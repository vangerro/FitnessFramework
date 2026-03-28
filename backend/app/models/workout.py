from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base

class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    date = Column(Date, nullable=False, index=True)

    # Eager-load exercises for detailed workout views.
    # Cascade delete ensures exercises are removed when the workout is removed.
    # Relationship is defined in `app.models.exercise`.

    exercises = relationship(
        "Exercise",
        back_populates="workout",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
