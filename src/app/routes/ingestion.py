from fastapi import APIRouter, UploadFile, Form, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.db.models import Document, DocumentEmbedding
from app.services.embedding_service import chunk_and_generate_embeddings, extract_text_from_pdf
import json
import uuid
from datetime import datetime
from typing import Optional

router = APIRouter()

@router.post("/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    metadata: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """API to ingest a document and store metadata & embeddings in PostgreSQL using ORM (Async)."""
    try:
        # Extract text from the uploaded PDF file
        extracted_text = await extract_text_from_pdf(file)
        metadata_json = json.loads(metadata) if metadata else {}

        # Create a new document record
        new_document = Document(
            title=title or file.filename,
            file_path=f"/storage/{uuid.uuid4()}.pdf",
            content=extracted_text,
            doc_metadata=metadata_json,
        )
        db.add(new_document)
        await db.commit()
        await db.refresh(new_document)

        # Chunk the extracted text and generate embeddings for the chunks
        chunks, chunk_embeddings = await chunk_and_generate_embeddings(extracted_text)

        # Create document embedding records for each chunk
        embedding_records = [
            DocumentEmbedding(
                document_id=new_document.id,
                chunk_index=i,
                embedding=emb,
                chunk_text=chunk,
            )
            for i, (chunk, emb) in enumerate(zip(chunks, chunk_embeddings))
        ]
        db.add_all(embedding_records)
        await db.commit()

        # Return success response with document details
        return {
            "document_id": new_document.id,
            "status": "success",
            "message": "Document successfully ingested.",
            "chunks_created": len(chunks),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        # Rollback the transaction in case of error
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
