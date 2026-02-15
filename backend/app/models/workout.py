from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, JSON
from sqlalchemy.sql import func
from app.db.base import Base

class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    plan_json = Column(JSON, nullable=False)  # enthält Struktur der Tage/Übungen
