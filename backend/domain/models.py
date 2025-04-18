from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid
from datetime import datetime
from repository.database import Base

class SessionStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TERMINATED = "terminated"

class UserRole(enum.Enum):
    HOST = "host"
    EDITOR = "editor"
    VIEWER = "viewer"

class Session(Base):
    __tablename__ = "sessions"
    
    session_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, nullable=False)
    host_user_id = Column(String, nullable=False)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    last_activity = Column(DateTime, default=func.now(), onupdate=func.now())
    status = Column(Enum(SessionStatus), default=SessionStatus.ACTIVE)
    max_participants = Column(Integer, default=10)
    is_public = Column(Boolean, default=True)
    session_timeout = Column(Integer, default=60)  # minutes
    
    participants = relationship("SessionParticipant", back_populates="session", cascade="all, delete-orphan")

class SessionParticipant(Base):
    __tablename__ = "session_participants"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String, ForeignKey("sessions.session_id", ondelete="CASCADE"))
    user_id = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.VIEWER)
    joined_at = Column(DateTime, default=func.now())
    last_active = Column(DateTime, default=func.now(), onupdate=func.now())
    
    session = relationship("Session", back_populates="participants")
