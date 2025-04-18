from ..constants import ACTION_DISCONNECTED, ACTION_JOINED

from .socket_manager import connected_room_socket_mapping, sio

"""
New client join event handler
"""
@sio.event
async def join(sid, data):
    global connected_room_socket_mapping

    room = data.get("roomId")
    username = data.get("username")
    print(f"[INFO] JOIN event from {sid} with username {username} in room {room}")
    if room and username:
        # add socket and username to current client list
        new_client = {"socketId": sid, "username": username}
        connected_room_socket_mapping.setdefault(room, []).append(new_client)

        # add sid to room
        await sio.enter_room(sid, room)

        # let all clients know about new joiner
        current_room = connected_room_socket_mapping.get(room, [])
        await sio.emit(
            ACTION_JOINED,
            {"clients": current_room, "username": username, "socketId": sid},
            room=room,
        )


"""
Client disconnect event handler
"""
@sio.event
async def leave(sid, data):
    # fetch all rooms
    rooms = sio.rooms(sid)
    print(f"LEAVE event from {sid} in rooms {rooms}")

    # for each room that the client is in
    for room in rooms:
        if room == sid:
            continue

        clients = connected_room_socket_mapping.get(room, [])
        client = next((c for c in clients if c.get("socketId") == sid), None)

        # If the client is found, remove it and update the mapping
        if client:
            username = client.get("username")
            clients.remove(client)

        # let all other clients in that room know that this particular client has left
        await sio.emit(
            ACTION_DISCONNECTED,
            {"socketId": sid, "username": username},
            room=room,
            skip_sid=sid,
        )
