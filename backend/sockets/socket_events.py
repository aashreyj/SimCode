import socketio
from constants import *

# define new socket handler
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="http://localhost:3000"
)

connected_room_socket_mapping = {}

"""
New client join event handler
"""
@sio.event
async def join(sid, data):
    room = data.get("roomId")
    username = data.get("username")
    print(f"JOIN event from {sid} with username {username} in room {room}")
    if room and username:
        # add socket and username to current client list
        if room in connected_room_socket_mapping:
            connected_room_socket_mapping[room].append({"socketId": sid, "username": username})
        else:
            connected_room_socket_mapping[room] = [{"socketId": sid, "username": username}]

        # add sid to room
        await sio.enter_room(sid, room)

        # let all clients know about new joiner
        current_room = connected_room_socket_mapping.get(room)
        await sio.emit(ACTION_JOINED, {
                "clients": current_room,
                "username": username,
                "socketId": sid
            }, room=room)
        
        # return list of clients to the new joiner
        

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

        # collect the username and index
        clients = connected_room_socket_mapping.get(room)
        username = ""
        index = -1
        for i, client in enumerate(clients):
            if client.get("socketId") == sid:
                username = client.get("username")
                index = i
                break

        # if found, delete the object and update the mapping
        if index >= 0:
            client = clients[index]
            clients.pop(index)
            del client

        # let all other clients in that room know that this particular client has left
        await sio.emit(ACTION_DISCONNECTED, {"socketId": sid, "username": username}, room=room, skip_sid=sid)

@sio.event
async def document_save(sid, data):
    room = data.get("roomId")
    document_id = data.get("documentId")
    title = data.get("title")
    
    print(f"DOCUMENT SAVE event from {sid} in room {room}")

    # Notify all room members about document save
    if room and document_id:
        await sio.emit("document_updated", {
            "documentId": document_id,
            "title": title
        }, room=room, skip_sid=sid)