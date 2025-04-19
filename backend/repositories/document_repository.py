# repositories/document_repository.py
import os
from db.database import Database
from models.document import Document, DocumentVersion
import json
import redis
import pickle


class DocumentRepository:
    def __init__(self):
        self.db = Database()
        # Initialize Redis cache
        self.cache = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=0,
            decode_responses=False
        )
        self.cache_ttl = 300  
    
    def _cache_key(self, doc_id):
        return f"document:{doc_id}"
    
    def find_by_id(self, doc_id):
        # Try to get from cache first
        cached_doc = self.cache.get(self._cache_key(doc_id))
        if cached_doc:
            return pickle.loads(cached_doc)
        
        # If not in cache, get from database
        try:
            cursor = self.db.get_cursor()
            
            # Get document metadata
            cursor.execute("""
                SELECT d.id, d.title, d.language, d.owner_id, d.created_at, d.updated_at, dc.content
                FROM documents d
                JOIN document_content dc ON d.id = dc.document_id
                WHERE d.id = %s
            """, (doc_id,))
            
            result = cursor.fetchone()
            if not result:
                return None
                
            document = Document(
                id=result['id'],
                title=result['title'],
                language=result['language'],
                content=result['content'],
                owner_id=result['owner_id'],
                created_at=result['created_at'],
                updated_at=result['updated_at']
            )
            
            # Cache the document
            self.cache.setex(
                self._cache_key(doc_id),
                self.cache_ttl,
                pickle.dumps(document)
            )
            
            return document
        except Exception as e:
            self.db.rollback()
            raise e
    
    def save(self, document):
        try:
            cursor = self.db.get_cursor()
            
            # Insert document metadata
            cursor.execute("""
                INSERT INTO documents (id, title, language, owner_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id, created_at, updated_at
            """, (document.id, document.title, document.language, document.owner_id))
            
            result = cursor.fetchone()
            document.id = result['id']
            document.created_at = result['created_at']
            document.updated_at = result['updated_at']
            
            # Insert document content
            cursor.execute("""
                INSERT INTO document_content (document_id, content)
                VALUES (%s, %s)
            """, (document.id, document.content))
            
            self.db.commit()
            
            # Cache the new document
            self.cache.setex(
                self._cache_key(document.id),
                self.cache_ttl,
                pickle.dumps(document)
            )
            
            return document
        except Exception as e:
            self.db.rollback()
            raise e
    
    def update(self, document):
        try:
            cursor = self.db.get_cursor()
            
            # Update document metadata
            cursor.execute("""
                UPDATE documents
                SET title = %s, language = %s
                WHERE id = %s
                RETURNING updated_at
            """, (document.title, document.language, document.id))
            
            if cursor.rowcount == 0:
                raise ValueError(f"Document with id {document.id} not found")
                
            result = cursor.fetchone()
            document.updated_at = result['updated_at']
            
            # Update document content
            cursor.execute("""
                UPDATE document_content
                SET content = %s
                WHERE document_id = %s
            """, (document.content, document.id))
            
            self.db.commit()
            
            # Update cache
            self.cache.setex(
                self._cache_key(document.id),
                self.cache_ttl,
                pickle.dumps(document)
            )
            
            return document
        except Exception as e:
            self.db.rollback()
            raise e
    
    def delete(self, doc_id):
        try:
            cursor = self.db.get_cursor()
            
            # Delete document (cascade will delete content and versions)
            cursor.execute("DELETE FROM documents WHERE id = %s", (doc_id,))
            
            self.db.commit()
            
            # Remove from cache
            self.cache.delete(self._cache_key(doc_id))
            
            return cursor.rowcount > 0
        except Exception as e:
            self.db.rollback()
            raise e
    
    def find_by_user(self, user_id, limit=20, offset=0):
        try:
            cursor = self.db.get_cursor()
            
            cursor.execute("""
                SELECT d.id, d.title, d.language, d.owner_id, d.created_at, d.updated_at
                FROM documents d
                WHERE d.owner_id = %s
                ORDER BY d.updated_at DESC
                LIMIT %s OFFSET %s
            """, (user_id, limit, offset))
            
            results = cursor.fetchall()
            documents = []
            
            for row in results:
                document = Document(
                    id=row['id'],
                    title=row['title'],
                    language=row['language'],
                    owner_id=row['owner_id'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    content=None  
                )
                documents.append(document)
                
            return documents
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_versions(self, doc_id, limit=10, offset=0):
        try:
            cursor = self.db.get_cursor()
            
            cursor.execute("""
                SELECT id, document_id, version_number, content_type, created_at, created_by
                FROM document_versions
                WHERE document_id = %s
                ORDER BY version_number DESC
                LIMIT %s OFFSET %s
            """, (doc_id, limit, offset))
            
            results = cursor.fetchall()
            versions = []
            
            for row in results:
                version = DocumentVersion(
                    id=row['id'],
                    document_id=row['document_id'],
                    version_number=row['version_number'],
                    content_type=row['content_type'],
                    created_at=row['created_at'],
                    created_by=row['created_by']
                )
                versions.append(version)
                
            return versions
        except Exception as e:
            self.db.rollback()
            raise e
    
    def save_version(self, version):
        try:
            cursor = self.db.get_cursor()
            
            # Get the latest version number for this document
            cursor.execute("""
                SELECT COALESCE(MAX(version_number), 0) as max_version
                FROM document_versions
                WHERE document_id = %s
            """, (version.document_id,))
            
            result = cursor.fetchone()
            next_version = result['max_version'] + 1
            
            # Insert the new version
            cursor.execute("""
                INSERT INTO document_versions 
                (document_id, version_number, content_type, content, base_version_id, created_by)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, created_at
            """, (
                version.document_id,
                next_version,
                version.content_type,
                version.content,
                version.base_version_id,
                version.created_by
            ))
            
            result = cursor.fetchone()
            version.id = result['id']
            version.created_at = result['created_at']
            version.version_number = next_version
            
            self.db.commit()
            return version
        except Exception as e:
            self.db.rollback()
            raise e
            
    def get_version_content(self, version_id):
        try:
            cursor = self.db.get_cursor()
            
            cursor.execute("""
                SELECT content, content_type, base_version_id
                FROM document_versions
                WHERE id = %s
            """, (version_id,))
            
            return cursor.fetchone()
        except Exception as e:
            self.db.rollback()
            raise e
        
    def restore_version(self, document_id, version_id, user_id):
        """
        Restore a document to a specific version
        """
        try:
            # Get the version content
            version_data = self.get_version_content(version_id)
            if not version_data:
                raise ValueError(f"Version {version_id} not found")
            
            # Get the document
            document = self.find_by_id(document_id)
            if not document:
                raise ValueError(f"Document {document_id} not found")
            
            # Save current state as a version before restoring
            current_version = DocumentVersion(
                document_id=document_id,
                content_type="text",
                content=document.content,
                created_by=user_id
            )
            self.save_version(current_version)
            
            # Update the document content with version content
            document.content = version_data['content']
            
            # Update the document
            updated_doc = self.update(document)
            
            # Clear cache to ensure latest content is fetched
            self.cache.delete(self._cache_key(document_id))
            
            return updated_doc
        except Exception as e:
            self.db.rollback()
            raise e