from models.document import Document, DocumentVersion
import uuid

class DocumentFactory:
    """Factory for creating documents and versions"""
    
    @staticmethod
    def create_document(title, language, owner_id, content=""):
        """Create a new document"""
        return Document(
            id=str(uuid.uuid4()),
            title=title,
            language=language,
            content=content,
            owner_id=owner_id
        )
    
    @staticmethod
    def create_version_from(document, user_id, version_strategy, previous_version=None):
        """Create a version of a document using the provided strategy"""
        return version_strategy.create_version(document, user_id, previous_version)