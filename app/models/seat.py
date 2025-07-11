from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.db import Base

class Seat(Base):
    __tablename__ = "seats"
    id = Column(Integer, primary_key=True, index=True)
    flight_id = Column(Integer, nullable=False)
    seat_number = Column(String, nullable=False)
    is_available = Column(Boolean, default=True)
