from sqlalchemy import Column, Integer, ForeignKey, Date, Numeric
from app.db.base import Base

class BodyMeasurement(Base):
    __tablename__ = "body_measurements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    chest = Column(Numeric(5, 2), nullable=False)
    waist = Column(Numeric(5, 2), nullable=False)
    arms = Column(Numeric(5, 2), nullable=False)
