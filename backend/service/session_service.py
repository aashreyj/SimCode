from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from domain import models, schemas
from repository.session_repository import SessionRepository
import uuid
import json
from datetime import datetime

class SessionService:
    @staticmethod
    def create_session(db: Session, session_data: schemas.SessionCreateRequest, host_user_id: str):
        """Create a new collaborative session"""
        session_dict = session_data.dict()
        session_dict["session_id"] = str(uuid.uuid4())
                
        # Create session and add host as participant
        session = SessionRepository.create_session(db, session_dict, host_user_id)
        
        return session
    
    @staticmethod
    def get_session(db: Session, session_id: str):
        """Get a session by ID"""
        session = SessionRepository.get_session_by_id(db, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session with ID {session_id} not found"
            )
        return session
    
    @staticmethod
    def get_user_sessions(db: Session, user_id: str):
        """Get all sessions for a user"""
        return SessionRepository.get_sessions_by_user(db, user_id)
    
    @staticmethod
    def update_session(db: Session, session_id: str, session_data: schemas.SessionUpdateRequest, user_id: str):
        """Update session details"""
        session = SessionService.get_session(db, session_id)
        
        # Check if user is the host
        if session.host_user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the session host can update session details"
            )
        
        # Update the session
        update_data = session_data.dict(exclude_unset=True)
        updated_session = SessionRepository.update_session(db, session, update_data)
        
        return updated_session
    
    @staticmethod
    def delete_session(db: Session, session_id: str, user_id: str):
        """Delete a session"""
        session = SessionService.get_session(db, session_id)
        
        # Check if user is the host
        if session.host_user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the session host can delete the session"
            )
        
        # Delete the session
        SessionRepository.delete_session(db, session)
        
        return {"message": f"Session {session_id} has been deleted"}
    
    @staticmethod
    def join_session(db: Session, session_id: str, join_data: schemas.SessionJoinRequest):
        """Join an existing session"""
        session = SessionService.get_session(db, session_id)
        
        # Check if session is active
        if session.status != models.SessionStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Session is {session.status.value} and cannot be joined"
            )
        
        # Check if user is already a participant
        existing_participant = SessionRepository.get_participant(db, session_id, join_data.user_id)
        
        if existing_participant:
            # Update last active time
            SessionRepository.update_participant(db, existing_participant, {"last_active": datetime.now()})
            return session
        
        # Check max participants
        if len(session.participants) >= session.max_participants:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Session has reached maximum capacity of {session.max_participants} participants"
            )
        
        # Determine role (can't join as host if not the session creator)
        role = join_data.role
        if role == schemas.UserRoleEnum.HOST and join_data.user_id != session.host_user_id:
            role = schemas.UserRoleEnum.VIEWER
        
        # Add participant
        user_data = {
            "user_id": join_data.user_id,
            "role": role,
        }
        
        SessionRepository.create_participant(db, session_id, user_data)
        
        # Update session last activity
        SessionRepository.update_session(db, session, {"last_activity": datetime.now()})
        
        # Get fresh session with updated participants
        return SessionService.get_session(db, session_id)
    
    @staticmethod
    def leave_session(db: Session, session_id: str, user_id: str):
        """Leave a session"""
        session = SessionService.get_session(db, session_id)
        
        participant = SessionRepository.get_participant(db, session_id, user_id)
        
        if not participant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} is not a participant in session {session_id}"
            )
        
        # Remove participant
        SessionRepository.remove_participant(db, participant)
        
        # If host is leaving, either transfer host role or mark session as inactive
        if user_id == session.host_user_id:
            # Get remaining participants
            remaining_participants = [p for p in session.participants if p.user_id != user_id]
            
            if remaining_participants:
                # Transfer host role to the first remaining participant
                new_host = remaining_participants[0]
                SessionRepository.update_participant(db, new_host, {"role": models.UserRole.HOST})
                SessionRepository.update_session(db, session, {"host_user_id": new_host.user_id})
            else:
                # No participants left, mark session as inactive
                SessionRepository.update_session(db, session, {"status": models.SessionStatus.INACTIVE})
        
        return {"message": f"User {user_id} has left session {session_id}"}
    
    @staticmethod
    def cleanup_inactive_sessions(db: Session):
        """Clean up sessions that have been inactive for longer than their timeout period"""
        inactive_sessions = SessionRepository.get_inactive_sessions(db)
        
        for session in inactive_sessions:
            SessionRepository.update_session(db, session, {"status": models.SessionStatus.INACTIVE})
        
        return {"message": f"Cleaned up {len(inactive_sessions)} inactive sessions"}