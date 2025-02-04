import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.services.qna_service import retrieve_similar_chunks, query_llm_with_context

# Initialize Logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

# API Endpoint for Retrieval
@router.get("/retrieve")
async def query_retrieval(
    query: str,
    top_k: int = 3,
    document_names: Optional[List[str]] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """
    API to retrieve the top_k most similar document chunks asynchronously.
    Supports optional filtering by document names.
    """
    try:
        retrieved_chunks = await retrieve_similar_chunks(query, top_k, db, document_names)

        return [
            {
                "document_name": row[0],
                "chunk_text": row[1],
                "similarity": round(row[2], 4),
            }
            for row in retrieved_chunks
        ]
    except Exception as e:
        logger.error(f"Error in query_retrieval: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve similar document chunks.")

# API Endpoint for Question Answering
@router.get("/query")
async def query_answering(
    query: str,
    document_names: Optional[List[str]] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """
    API to retrieve relevant document chunks and generate answers using the LLM.
    """
    try:
        retrieved_chunks = await retrieve_similar_chunks(query, top_k=3, db=db, document_names=document_names)

        # Query LLM with retrieved document context
        answer = await query_llm_with_context(query, retrieved_chunks)

        return {
            "query": query,
            "answer": answer,
        }
    except Exception as e:
        logger.error(f"Error in query_answering: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate an answer.")
