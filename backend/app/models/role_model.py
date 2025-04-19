from sqlalchemy import Column, String
from sqlalchemy.orm import Session
from app.models.base import Base

class Role(Base):
    __tablename__ = "roles"

    role_type = Column(String, primary_key=True)  # e.g., 'host', 'editor', 'viewer'
