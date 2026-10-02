from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from database import Base

# SQLAlchemy Model
class TaskDB(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    status = Column(String, default="To Do")
    priority = Column(String, default="Medium")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Pydantic Schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "To Do"
    priority: Optional[str] = "Medium"

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None

class TaskResponse(TaskBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
