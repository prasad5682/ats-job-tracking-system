from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class ApplicationHistory(Base):
    __tablename__ = "application_history"

    id = Column(Integer, primary_key=True, index=True)

    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    old_stage = Column(String, nullable=False)
    new_stage = Column(String, nullable=False)

    changed_by = Column(Integer, ForeignKey("users.id"))
    changed_at = Column(DateTime, default=datetime.utcnow)

    # ✅ BIDIRECTIONAL LINKS
    application = relationship("Application", back_populates="history")
    user = relationship("User")
