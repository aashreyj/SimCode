from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from fastapi.responses import JSONResponse
from sockets.socket_events import connected_room_socket_mapping
from sqlalchemy.orm import Session
from repository.database import get_db
from domain import schemas
from service.session_service import SessionService
from fastapi.encoders import jsonable_encoder
from api.dependencies import get_current_user
from typing import List


router = APIRouter(
    prefix="/sessions",
    tags=["sessions"],
    responses={404: {"description": "Not found"}}
)

# Create a new session
@router.post("/", response_model=schemas.SessionResponse)
async def create_session(
    session_data: schemas.SessionCreateRequest,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Create a new collaborative session"""
    session = SessionService.create_session(db, session_data, current_user)
    return session

# Get session details
@router.get("/{session_id}", response_model=schemas.SessionResponse)
async def get_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get details about a specific session"""
    session = SessionService.get_session(db, session_id)
    return session

# Get all sessions for current user
@router.get("/", response_model=List[schemas.SessionResponse])
async def get_user_sessions(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Get all sessions for the current user"""
    sessions = SessionService.get_user_sessions(db, current_user)
    return sessions

# Update session details
@router.put("/{session_id}", response_model=schemas.SessionResponse)
async def update_session(
    session_id: str,
    session_data: schemas.SessionUpdateRequest,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Update session details (host only)"""
    session = SessionService.update_session(db, session_id, session_data, current_user)
    return session

# Delete a session
@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Delete a session (host only)"""
    return SessionService.delete_session(db, session_id, current_user)

# Join a session
@router.post("/join")
async def join_room_combined(
    roomId: str,
    join_data: schemas.SessionJoinRequest,
    db: Session = Depends(get_db)
):
    # First check live connected users count
    member_count = len(connected_room_socket_mapping.get(roomId)) if roomId in connected_room_socket_mapping else 0
    max_allowed = 8  # or fetch from session details if it's dynamic

    if member_count >= max_allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Room is full"
        )

    # Then check session existence and handle join via SessionService
    try:
        session = SessionService.get_session(db, roomId)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {roomId} not found"
        )

    # Now actually join user to session via service
    try:
        joined_session = SessionService.join_session(db, roomId, join_data)
        joined_session_schema = schemas.SessionResponse.from_orm(joined_session)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not join session: {str(e)}"
        )
        
    response_content = {
        "message": f"Joined room {roomId} successfully",
        "session_details": joined_session_schema,
        "current_member_count": member_count + 1,
        "max_allowed": max_allowed
    }

    return JSONResponse(content=jsonable_encoder(response_content))

# Leave a session
@router.post("/leave/{session_id}")
async def leave_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Leave a session"""
    result = SessionService.leave_session(db, session_id, current_user)
    return result

# Scheduled task to clean up inactive sessions
@router.post("/cleanup")
async def cleanup_sessions(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Clean up inactive sessions (admin only)"""
    # Run cleanup in background to avoid blocking
    background_tasks.add_task(SessionService.cleanup_inactive_sessions, db)
    return {"status": "Cleanup task scheduled"}
