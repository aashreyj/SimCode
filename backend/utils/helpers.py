import json
from datetime import datetime, timedelta

def format_session_response(session, participants=None):
    """Format a session object and its participants for API response"""
    if participants is None:
        participants = session.participants
    
    return {
        "session_id": session.session_id,
        "document_id": session.document_id,
        "host_user_id": session.host_user_id,
        "name": session.name,
        "created_at": session.created_at.isoformat(),
        "last_activity": session.last_activity.isoformat(),
        "status": session.status.value,
        "max_participants": session.max_participants,
        "is_public": session.is_public,
        "session_timeout": session.session_timeout,
        "participants": [format_participant_response(p) for p in participants]
    }

def format_participant_response(participant):
    """Format a participant object for API response"""
    return {
        "user_id": participant.user_id,
        "role": participant.role.value,
        "joined_at": participant.joined_at.isoformat(),
        "last_active": participant.last_active.isoformat()
    }
