from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(String(300), nullable=True)
    priority = Column(String(20), nullable=False, default="Medium")
    is_completed = Column(Boolean, nullable=False, default=False)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now)