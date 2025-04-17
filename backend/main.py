import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sockets.socket_events import sio
from api.code import router as code_router
from api.room import router as room_router

# Wrap FastAPI with the Socket.IO ASGI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Include HTTP routes
app.include_router(code_router, prefix='/api')
app.include_router(room_router, prefix='/api')

# Setup Socket Routes
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)
