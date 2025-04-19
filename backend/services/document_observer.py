from services.document_service import DocumentObserver
from fastapi import WebSocket
import json

class WebSocketDocumentObserver(DocumentObserver):
    """Observer that sends document updates to connected websocket clients"""
    
    def __init__(self):
        self.connections = {}
    
    def register_connection(self, document_id, websocket):
        """Register a websocket connection for a document"""
        if document_id not in self.connections:
            self.connections[document_id] = []
        
        if websocket not in self.connections[document_id]:
            self.connections[document_id].append(websocket)
    
    def remove_connection(self, document_id, websocket):
        """Remove a websocket connection"""
        if document_id in self.connections and websocket in self.connections[document_id]:
            self.connections[document_id].remove(websocket)
            
            if not self.connections[document_id]:
                del self.connections[document_id]
    
    async def on_document_changed(self, document):
        """Notify all connected clients about document changes"""
        document_id = document.id
        if document_id not in self.connections:
            return
            
        # Prepare message to send
        message = {
            "type": "document_update",
            "document": {
                "id": document.id,
                "title": document.title,
                "content": document.content,
                "updated_at": document.updated_at.isoformat() if document.updated_at else None
            }
        }
        
        # Send to all connected clients for this document
        disconnected = []
        for websocket in self.connections[document_id]:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception:
                # Mark this connection for removal
                disconnected.append(websocket)
        
        for websocket in disconnected:
            self.remove_connection(document_id, websocket)