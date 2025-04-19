# models/document.py
import uuid
from datetime import datetime

class Document:
    def __init__(self, id=None, title="", language="plaintext", content="", owner_id=None, 
                 created_at=None, updated_at=None):
        self.id = id or str(uuid.uuid4())
        self.title = title
        self.language = language
        self.content = content
        self.owner_id = owner_id
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "language": self.language,
            "content": self.content,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            title=data.get("title", ""),
            language=data.get("language", "plaintext"),
            content=data.get("content", ""),
            owner_id=data.get("owner_id"),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else None
        )


class DocumentVersion:
    def __init__(self, id=None, document_id=None, version_number=None, content_type="full",
                 content=None, base_version_id=None, created_at=None, created_by=None):
        self.id = id or str(uuid.uuid4())
        self.document_id = document_id
        self.version_number = version_number
        self.content_type = content_type  # 'full' or 'diff'
        self.content = content
        self.base_version_id = base_version_id
        self.created_at = created_at or datetime.now()
        self.created_by = created_by
        
    def to_dict(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "version_number": self.version_number,
            "content_type": self.content_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by
        }