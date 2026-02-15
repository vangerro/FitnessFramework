from sqlalchemy import Column, Integer, ForeignKey, Date, Numeric
from app.db.base import Base

class WeightEntry(Base):
    __tablename__ = "weight_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    weight = Column(Numeric(5,2), nullable=False)
    body_fat = Column(Numeric(5,2), nullable=True)
