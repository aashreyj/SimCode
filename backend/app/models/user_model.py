from sqlalchemy import Column, Integer, String, ForeignKey
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    # role = Column(String, nullable=False)
    role_of_user = Column(String, ForeignKey("roles.role_type"), nullable=False)


