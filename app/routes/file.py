from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException
from app.db import get_db
from app.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.vector_service import save_uploaded_document, store_document, search_document
from app.security import verify_api_key

files_router = APIRouter( prefix="/files", tags=["files"], dependencies=[Depends(verify_api_key)])

ALLOWED_TYPES = {
    "application/pdf",
    "text/plain",
    "text/markdown",
    "text/csv",
    "application/json",
}
MAX_MB = 20

@files_router.post('/upload')
async def upload_file( file: UploadFile = File(...), session_id: str = Query(...),db: AsyncSession = Depends(get_db)):

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"File type '{file.content_type}' not supported")

    content = await file.read()
    size_mb = len(content) /1024 /1024

    if size_mb > MAX_MB:
        raise HTTPException(400, f"File too large ({size_mb:.1f}MB). Max {MAX_MB}MB")

    # save to disk
    filepath = await save_uploaded_document(content, file.filename)

    # chunk → embed → store in pgvector
    chunks = await store_document(db, filepath, file.filename, session_id)

    return {
        "filename": file.filename,
        "size_mb": round(size_mb, 2),
        "chunks_indexed": chunks,
        "message": f"Indexed into {chunks} searchable chunks",
    }