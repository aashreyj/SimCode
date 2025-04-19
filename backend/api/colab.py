#presentation/websockets_endpoints.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from service.collab_service import CollaborationService

router = APIRouter()
collab_service = CollaborationService()

@router.websocket("/ws/{room_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_id: str):
    # await websocket.accept()
    try:
        await collab_service.handle_connection(websocket, room_id, user_id)
    except WebSocketDisconnect:
        await collab_service.handle_disconnect(websocket, room_id, user_id)
