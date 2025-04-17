import socketio
from fastapi import FastAPI
from sockets.socket_events import sio
from api.code import router as code_router

# Wrap FastAPI with the Socket.IO ASGI app
app = FastAPI()

# Include HTTP routes
app.include_router(code_router, prefix='/api')

# Setup Socket Routes
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)
