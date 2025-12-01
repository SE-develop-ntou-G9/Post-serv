from sqlalchemy import (
    Column, String, Enum, DateTime, Boolean, Text, Integer, JSON, Index, func
    , text
)
from sqlalchemy.dialects.mysql import JSON as MySQLJSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DriverPost(Base):
    __tablename__ = 'driver_posts'

    id = Column(String(36), primary_key=True, autoincrement=False)

    driver_id = Column(String(255), nullable=False, index=True)
    client_id = Column(String(255), nullable=False, index=True, server_default=text("'unknown'"))
    vehicle_info = Column(String(255), nullable=True)

    status = Column(
        Enum("open", "matched", "closed", name="driver_post_status"),
        nullable=False,
        server_default="open",
        index=True,
    )

    time_stamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    start_point = Column(MySQLJSON, nullable=False)
    destination = Column(MySQLJSON, nullable=False)

    meet_point = Column(MySQLJSON, nullable=False)
    departure_time = Column(DateTime(timezone=True), nullable=False)
    notes = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    helmet = Column(Boolean, nullable=False, server_default="0")
    contact = Column(MySQLJSON, nullable=False)  # contact_info
    leave = Column(Boolean, nullable=False, server_default="0")

    __table_args__ = (
        Index("ix_driver_posts_driver_status", "driver_id", "status"),
    )
