from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)

    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)

    stage = Column(String, default="Applied")
    created_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("User")
    job = relationship("Job")

    history = relationship("ApplicationHistory", back_populates="application")
