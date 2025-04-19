# services/document_service.py
from repositories.document_repository import DocumentRepository
from services.document_factory import DocumentFactory
from services.version_strategies import FullSnapshotStrategy, DiffStrategy
import uuid
import logging
from models.document import DocumentVersion, Document


class DocumentService:
    def __init__(self):
        self.document_repository = DocumentRepository()
    
    def get_document(self, doc_id):
        """Get a document by ID"""
        return self.document_repository.find_by_id(doc_id)
    
    def create_document(self, title, language, owner_id, content=""):
        """Create a new document"""
        document = Document(
            id=str(uuid.uuid4()),
            title=title,
            language=language,
            owner_id=owner_id,
            content=content
        )
        return self.document_repository.save(document)
    
    def update_document(self, doc_id, content, user_id, title=None, language=None, create_version=False):
        """
        Update a document and optionally create a version
        
        Args:
            doc_id (str): Document ID
            content (str): New content
            user_id (str): User ID
            title (str, optional): New title
            language (str, optional): New language
            create_version (bool): Whether to create a version
        """
        # Get current document to save the version before updating
        document = self.get_document(doc_id)
        
        if not document:
            raise ValueError(f"Document with id {doc_id} not found")
        
        # Create a version if requested BEFORE updating the document
        if create_version:
            print(f"Creating version for document {doc_id}")
            version = DocumentVersion(
                id=str(uuid.uuid4()),
                document_id=doc_id,
                version_number=None,  
                content_type="text",
                content=document.content,  
                base_version_id=None,
                created_by=user_id,
                created_at=None 
            )
            self.document_repository.save_version(version)
        
        # Update document fields if provided
        if title is not None:
            document.title = title
        if language is not None:
            document.language = language
        document.content = content
        
        # Update the document
        updated_doc = self.document_repository.update(document)
        return updated_doc
    
    def get_document_list(self, user_id, limit=20, offset=0):
        """Get list of documents for a user"""
        return self.document_repository.find_by_user(user_id, limit, offset)
    
    def get_document_versions(self, doc_id, limit=10, offset=0):
        """Get versions of a document"""
        return self.document_repository.get_versions(doc_id, limit, offset)
    
     
    def restore_version(self, doc_id, version_id, user_id, create_backup_version=True):
        """
        Restore a document to a specific version
        
        Args:
            doc_id (str): Document ID  
            version_id (str): Version ID to restore
            user_id (str): User ID
            create_backup_version (bool): Whether to create a backup version of current state
        """
        document = self.get_document(doc_id)
        if not document:
            raise ValueError(f"Document with id {doc_id} not found")
        
        # Get version content data
        version_data = self.document_repository.get_version_content(version_id)
        if not version_data:
            raise ValueError(f"Version with id {version_id} not found")
        
        # Save current state as a version if requested
        if create_backup_version:
            current_version = DocumentVersion(
                id=str(uuid.uuid4()),
                document_id=doc_id,
                version_number=None,  
                content_type="text",
                content=document.content,
                base_version_id=None,
                created_by=user_id,
                created_at=None  
            )
            self.document_repository.save_version(current_version)
        
        # Update document with version content
        document.content = version_data['content']
        updated_doc = self.document_repository.update(document)
        return updated_doc
        
    def delete_document(self, doc_id):
        """Delete a document"""
        return self.document_repository.delete(doc_id)
    
    def get_version_content(self, version_id):
        """Get content of a specific version without restoring it"""
        return self.document_repository.get_version_content(version_id)
    
  