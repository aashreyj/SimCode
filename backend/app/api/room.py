from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ..sockets.socket_manager import connected_room_socket_mapping

router = APIRouter()

"""
This endpoint is used to get the number of users in a room.
"""
@router.get("/room-user-count")
async def return_count(roomId: str = None):
    global connected_room_socket_mapping

    return JSONResponse(
        {
            "member_count": (
                len(connected_room_socket_mapping.get(roomId))
                if roomId in connected_room_socket_mapping
                else 0
            )
        }
    )
