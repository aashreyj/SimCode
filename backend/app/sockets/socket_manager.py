import socketio

from ..constants import FRONTEND_URL

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=FRONTEND_URL)
connected_room_socket_mapping = {}
from .code_events import *
from .room_events import *
