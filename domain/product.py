from sqlalchemy import UUID, Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship
import uuid

Base = declarative_base()


class DriverPost(Base):
    __tablename__ = 'driver_posts'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    driver_id = Column(Integer)
    vehicle_info = Column(String(255))
    status = Column(String(50))
    time_stamp = Column(String(50))
    start_point = Column(JSON)
    destination = Column(JSON)