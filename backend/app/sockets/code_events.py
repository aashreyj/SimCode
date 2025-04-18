from ..constants import ACTION_CODE_CHANGE, ACTION_LANG_CHANGE, ACTION_CODE_EXECUTED, ACTION_PREREQ_CHANGE

from .socket_manager import sio

"""
Code change event handler
"""
@sio.event
async def code_change(sid, data):
    room = data.get("roomId", "")
    code = data.get("code", "")
    print(f"CODE CHANGE event from {sid} in room {room}")

    # send updated code to all clients
    if room:
        await sio.emit(ACTION_CODE_CHANGE, {"code": code}, room=room, skip_sid=sid)


"""
Code sync event handler
"""
@sio.event
async def sync_code(sid, data):
    socket_id = data.get("socketId", "")
    prereq = data.get("prerequisites", "")
    code = data.get("code", "")
    lang = data.get("lang", "")
    print(f"SYNC CODE event from {sid} to {socket_id}")

    # send the latest code to the newly-joined socket
    if socket_id:
        await sio.emit(ACTION_PREREQ_CHANGE, {"prereq": prereq}, to=socket_id)
        await sio.emit(ACTION_CODE_CHANGE, {"code": code}, to=socket_id)
        await sio.emit(ACTION_LANG_CHANGE, {"lang": lang}, to=socket_id)


"""
Prerequisite change event handler
"""
@sio.event
async def prereq_change(sid, data):
    room = data.get("roomId")
    prereq = data.get("prerequisites")
    print(f"PREREQ CHANGE event from {sid} in room {room}")

    # send updated prereqs to all clients
    if room:
        await sio.emit(ACTION_PREREQ_CHANGE, {"prereq": prereq}, room=room, skip_sid=sid)


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


"""
Code execution handler
"""
@sio.event
async def code_executed(sid, data):
    room = data.get("roomId")
    stdout = data.get("stdout")
    stderr = data.get("stderr")
    print(f"CODE EXECUTED event from {sid} in room {room}")

    if room:
        await sio.emit(ACTION_CODE_EXECUTED, {"stdout": stdout, "stderr": stderr}, room=room, skip_sid=sid)
