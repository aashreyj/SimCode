from ..constants import ACTION_CODE_CHANGE, ACTION_LANG_CHANGE

from .socket_manager import sio

"""
Code change event handler
"""
@sio.event
async def code_change(sid, data):
    room = data.get("roomId")
    code = data.get("code")
    print(f"CODE CHANGE event from {sid} in room {room}")

    # send updated code to all clients
    if room and code:
        await sio.emit(ACTION_CODE_CHANGE, {"code": code}, room=room, skip_sid=sid)


"""
Code sync event handler
"""
@sio.event
async def sync_code(sid, data):
    socket_id = data.get("socketId")
    code = data.get("code")
    print(f"SYNC CODE event from {sid} to {socket_id}")

    # send the latest code to the newly-joined socket
    if socket_id and code:
        await sio.emit(ACTION_CODE_CHANGE, {"code": code}, to=socket_id)


"""
Code editor language change handler
"""
@sio.event
async def lang_change(sid, data):
    room = data.get("roomId")
    lang = data.get("lang")
    print(f"LANG CHANGE event from {sid} in room {room} for language {lang}")

    if room and lang:
        await sio.emit(ACTION_LANG_CHANGE, {"lang": lang}, room=room)
