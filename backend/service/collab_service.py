from typing import Dict
from fastapi import WebSocket
from asyncio import CancelledError
from core.sync_engine import SyncEngine
from service.connection_manager import ConnectionManager
from random import choice

class CollaborationService:
    def __init__(self):
        self.connection_manager = ConnectionManager()
        self.sync_engines: Dict[str, SyncEngine] = {}
        self.user_colors: Dict[str, Dict[str, str]] = {}
    
    def generate_unique_color(self, room_id: str) -> str:
        available_colors = [
            "#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#A133FF",
            "#33FFF6", "#FFD433", "#FF3333", "#33FF8A", "#8A33FF"
        ]
        assigned_colors = set(self.user_colors.get(room_id, {}).values())
        remaining_colors = list(set(available_colors) - assigned_colors)
        return choice(remaining_colors) if remaining_colors else "#000000"  # fallback to black


    async def handle_connection(self, websocket: WebSocket, room_id: str, user_id: str):
        await websocket.accept()

        if room_id not in self.sync_engines:
            self.sync_engines[room_id] = SyncEngine(room_id)

        if room_id not in self.user_colors:
            self.user_colors[room_id] = {}

        if user_id not in self.user_colors[room_id]:
            self.user_colors[room_id][user_id] = self.generate_unique_color(room_id)

        await self.connection_manager.connect(websocket, room_id, user_id,self.user_colors[room_id][user_id] )

        document = self.sync_engines[room_id].get_snapshot()
        active_users = self.sync_engines[room_id].get_active_users()
        # await websocket.send_json({"type": "user_list", "users": active_users})
        color_mapping = self.user_colors[room_id]
        cursor_positions =self.sync_engines[room_id].get_cursor_positions()
        print("INIT CUR",cursor_positions)
        await websocket.send_json({
            "type": "initial_state",
            "document_snapshot": document,
            "users": active_users,
            "user_colors": color_mapping,
        })

        try:
            while True:
                # data = await websocket.receive_json()
                # result = self.sync_engines[room_id].apply_user_edit(user_id, data)
                # await self.connection_manager.broadcast(room_id, result, sender_id=user_id)
                data = await websocket.receive_json()
                print("DATA",data)
                if data["type"] == "operation":
                    broadcast_message = self.sync_engines[room_id].apply_user_edit(
                        user_id, data
                    )
                    print("BROAD",broadcast_message)
                    await self.connection_manager.broadcast(
                        room_id, broadcast_message, sender_id=user_id
                    )

                elif data["type"]=="colors":
                    cursor_message=self.user_colors[room_id]
                    print("COL CUR",cursor_message)
                    await self.connection_manager.broadcast(room_id, cursor_message, sender_id=user_id)

                elif data["type"] == "cursor":
                    position = data.get("position")
                    print("CUR POS:",position)
                    if position is not None:
                        cursor_message = self.sync_engines[room_id].update_cursor(user_id, position)
                        print("CURSOR MSG",cursor_message)
                        await self.connection_manager.broadcast(room_id, cursor_message, sender_id=user_id)

                elif data["type"] == "leave":
                    await self.connection_manager.disconnect(websocket, room_id, user_id)
                    self.sync_engines[room_id].remove_user(user_id)
                    break

        except CancelledError:
            print(f"[DISCONNECT] {user_id} was cancelled from room {room_id}")
            await self.handle_disconnect(websocket, room_id, user_id)
            raise  # optional, re-raise if you want to propagate cancellation

        except Exception as e:
            print(f"[ERROR] WebSocket error: {e}")
            await self.handle_disconnect(websocket, room_id, user_id)

    async def handle_disconnect(self, websocket: WebSocket, room_id: str, user_id: str):
        self.sync_engines[room_id].remove_user(user_id)
        await self.connection_manager.disconnect(websocket, room_id, user_id)
        self.user_colors[room_id].pop(user_id, None)
    
    async def handle_leave(self, websocket: WebSocket, room_id: str, user_id: str):
        print(f"[LEAVE] {user_id} is leaving room {room_id}")
        self.sync_engines[room_id].remove_user(user_id)
        await self.connection_manager.disconnect(websocket, room_id, user_id)
        self.user_colors[room_id].pop(user_id, None)