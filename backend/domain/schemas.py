from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserRoleEnum(str, Enum):
    HOST = "host"
    EDITOR = "editor"
    VIEWER = "viewer"

class SessionStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TERMINATED = "terminated"

class SessionCreateRequest(BaseModel):
    document_id: str
    name: Optional[str] = None
    max_participants: Optional[int] = 10
    is_public: Optional[bool] = True
    session_timeout: Optional[int] = 60  # minutes

class SessionJoinRequest(BaseModel):
    user_id: str
    role: Optional[UserRoleEnum] = UserRoleEnum.EDITOR

class SessionUpdateRequest(BaseModel):
    name: Optional[str] = None
    status: Optional[SessionStatusEnum] = None
    max_participants: Optional[int] = None
    is_public: Optional[bool] = None
    session_timeout: Optional[int] = None

class ParticipantResponse(BaseModel):
    user_id: str
    role: UserRoleEnum
    joined_at: datetime
    last_active: datetime

    model_config = ConfigDict(from_attributes=True)

class SessionResponse(BaseModel):
    session_id: str
    document_id: str
    host_user_id: str
    name: Optional[str] = None
    created_at: datetime
    last_activity: datetime
    status: SessionStatusEnum
    max_participants: int
    is_public: bool
    session_timeout: int
    participants: list[ParticipantResponse]

    model_config = ConfigDict(from_attributes=True)
