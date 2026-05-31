from sqlalchemy import Column, String, Float, Boolean, Integer

from app.database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True)
    store_id = Column(String, index=True)
    visitor_id = Column(String, index=True)
    camera_id = Column(String)
    event_type = Column(String)
    timestamp = Column(String)
    zone_id = Column(String)
    dwell_seconds = Column(Float)
    is_staff = Column(Boolean)
    confidence = Column(Float)