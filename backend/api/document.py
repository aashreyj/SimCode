from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
import uuid
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import json

from services.document_service import DocumentService

router = APIRouter()
document_service = DocumentService()

class DocumentCreate(BaseModel):
    title: str
    language: str
    content: str = ""

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    language: Optional[str] = None
    content: Optional[str] = None

class DocumentResponse(BaseModel):
    id: str
    title: str
    language: str
    content: Optional[str]
    owner_id: str
    created_at: str
    updated_at: str

class DocumentListResponse(BaseModel):
    id: str
    title: str
    language: str
    owner_id: str
    created_at: str
    updated_at: str

class VersionResponse(BaseModel):
    id: str
    document_id: str
    version_number: int
    content_type: str
    created_at: str
    created_by: str

def get_current_user():
    # For demo purposes only 
    return {"id":"11111111-1111-1111-1111-111111111111"}

@router.get("/{doc_id}")
async def get_document(doc_id: str):
    """Get a document by ID"""
    document = document_service.get_document(doc_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return document.to_dict()

@router.post("")
async def create_document(doc: DocumentCreate):
    """Create a new document"""
    # For demo - replace with actual auth
    current_user = get_current_user()
    
    try:
        document = document_service.create_document(
            title=doc.title,
            language=doc.language,
            owner_id=current_user["id"],
            content=doc.content
        )
        return document.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{doc_id}")
async def update_document(
    doc_id: str, 
    doc_update: DocumentUpdate, 
    create_version: bool = Query(False)  
):
    """Update a document"""
    # For demo - replace with actual auth
    current_user = get_current_user()
    
    document = document_service.get_document(doc_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    try:        
        updated_doc = document_service.update_document(
            doc_id=doc_id,
            content=doc_update.content if doc_update.content is not None else document.content,
            user_id=current_user["id"],
            title=doc_update.title,
            language=doc_update.language,
            create_version=create_version
        )
        return updated_doc.to_dict()
    except Exception as e:
        import traceback
        print(f"Error updating document: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
@router.get("")
async def get_documents(limit: int = 20, offset: int = 0):
    """Get list of documents for the current user"""
    # For demo - replace with actual auth
    current_user = get_current_user()
    
    try:
        documents = document_service.get_document_list(current_user["id"], limit, offset)
        return [doc.to_dict() for doc in documents]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{doc_id}/versions")
async def get_document_versions(doc_id: str, limit: int = 10, offset: int = 0):
    """Get versions of a document"""
    # For demo - replace with actual auth
    current_user = get_current_user()
    
    document = document_service.get_document(doc_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    try:
        versions = document_service.get_document_versions(doc_id, limit, offset)
        return [ver.to_dict() for ver in versions]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{doc_id}/restore/{version_id}")
async def restore_version(doc_id: str, version_id: str, create_backup: bool = Query(True)):
    """Restore a document to a specific version"""
    # For demo - replace with actual auth
    current_user = get_current_user()
    
    document = document_service.get_document(doc_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    try:
        restored_doc = document_service.restore_version(
            doc_id, 
            version_id, 
            current_user["id"],
            create_backup_version=create_backup
        )
        return restored_doc.to_dict()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document"""
    # For demo - replace with actual auth
    current_user = get_current_user()
    
    document = document_service.get_document(doc_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if the user has permission to delete the document
    if document.owner_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this document"
        )
    
    try:
        success = document_service.delete_document(doc_id)
        if success:
            return JSONResponse(content={"message": "Document deleted successfully"})
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete document"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
@router.get("/{doc_id}/versions/{version_id}/content")
async def get_version_content(doc_id: str, version_id: str):
    """Get content of a specific version without restoring it"""
    # For demo - replace with actual auth
    current_user = get_current_user()
    
    document = document_service.get_document(doc_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    try:
        version_data = document_service.get_version_content(version_id)
        if not version_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Version not found"
            )
        return {"content": version_data.get("content")}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )