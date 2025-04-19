from typing import Dict, Set
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}  # room_id -> user_id -> WebSocket
        self.active_users: Dict[str, Set[str]] = {}  # room_id -> set of user_ids
        self.user_colors: Dict[str, Dict[str, str]] = {}
    async def connect(self, websocket: WebSocket, room_id: str, user_id: str, color:str):
        if room_id not in self.user_colors:
            self.user_colors[room_id] = {}
        self.user_colors[room_id][user_id] = color
        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
            self.active_users[room_id] = set()

        self.active_connections[room_id][user_id] = websocket
        self.active_users[room_id].add(user_id)
        self.user_colors[room_id][user_id] = color
        print(f"[CONNECT] {user_id} joined room {room_id}")

        await self.broadcast_user_list(room_id)

    async def disconnect(self, websocket: WebSocket, room_id: str, user_id: str):
        if room_id in self.active_connections and user_id in self.active_connections[room_id]:
            del self.active_connections[room_id][user_id]
            self.active_users[room_id].discard(user_id)
            # self.user_colors[user_id]
            del self.user_colors[room_id][user_id]
            print(f"[DISCONNECT] {user_id} left room {room_id}")

            # Clean up if room becomes empty
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
                del self.active_users[room_id]
                del self.user_colors[room_id]
            else:
                await self.broadcast_user_list(room_id)


    async def broadcast_user_list(self, room_id: str):
        users = list(self.active_users.get(room_id, []))
        user_colors = self.user_colors.get(room_id, {})
        await self.broadcast(room_id, {
            "type": "user_list",
            "users": users,
            "user_colors":user_colors
        })

    async def broadcast(self, room_id: str, message: dict, sender_id: str = None):
        if room_id in self.active_connections:
            for uid, ws in self.active_connections[room_id].items():
                if uid != sender_id:  # optional: avoid echo
                    await ws.send_json(message)

    def get_users_in_room(self, room_id: str):
        return list(self.active_users.get(room_id, []))
