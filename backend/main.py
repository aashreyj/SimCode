import socketio
from app.api.code import router as code_router
from app.api.room import router as room_router
from app.constants import FRONTEND_URL
from app.sockets.socket_manager import sio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import engine
from app.models.user_model import Base
from app.api import user_routes
from app.models.base import Base

# Wrap FastAPI with the Socket.IO ASGI app
app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Include HTTP routes
app.include_router(code_router, prefix="/api")
app.include_router(room_router, prefix="/api")
app.include_router(user_routes.router)

# Setup Socket Routes
simcode = socketio.ASGIApp(sio, other_asgi_app=app)
