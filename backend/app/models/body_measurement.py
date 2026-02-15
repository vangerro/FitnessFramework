from sqlalchemy import Column, Integer, ForeignKey, Date, Numeric
from app.db.base import Base

class BodyMeasurement(Base):
    __tablename__ = "body_measurements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    neck = Column(Numeric(5,2), nullable=True)
    shoulders = Column(Numeric(5,2), nullable=True)
    chest = Column(Numeric(5,2), nullable=True)
    waist = Column(Numeric(5,2), nullable=True)
    hips = Column(Numeric(5,2), nullable=True)
    arm = Column(Numeric(5,2), nullable=True)
    thigh = Column(Numeric(5,2), nullable=True)
    calf = Column(Numeric(5,2), nullable=True)
