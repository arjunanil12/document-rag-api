import logging
from functools import lru_cache
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from fastapi import HTTPException
from app.llm.llm_initializer import LLMService
from app.services.embedding_service import embedding_model
from app.services.prompt_templates import QA_TEMPLATE

# Initialize Logger
logger = logging.getLogger(__name__)

# Initialize LLM Model Singleton
llm_instance = LLMService()
llm_model = llm_instance.get_llm()

@lru_cache(maxsize=1000)
def get_text_embedding_cached(text: str):
    """Caches text embeddings to reduce redundant computations."""
    return embedding_model.get_text_embedding(text)

async def retrieve_similar_chunks(
    query: str, top_k: int, db: AsyncSession, document_names: Optional[List[str]] = None
):
    """
    Retrieve top_k most similar document chunks asynchronously using pgvector.
    Supports optional filtering by document names.
    """
    try:
        logger.debug("Generating Query Embedding...")
        query_embedding = get_text_embedding_cached(query)

        if not query_embedding:
            raise HTTPException(status_code=400, detail="Failed to generate query embedding.")

        logger.debug(f"Query Embedding Sample: {query_embedding[:5]}... (Total {len(query_embedding)})")

        # Convert embedding to PostgreSQL-compatible format
        query_embedding_str = ",".join(map(str, query_embedding))

        # Construct SQL query with optional document name filtering
        base_query = """
            SELECT documents.title, document_embeddings.chunk_text, 
                   1 - (document_embeddings.embedding <=> ARRAY[{}]::vector) AS similarity
            FROM document_embeddings
            JOIN documents ON document_embeddings.document_id = documents.id
        """.format(query_embedding_str)

        query_params = {"top_k": top_k}

        if document_names:
            base_query += " WHERE documents.title = ANY(:document_names)"
            query_params["document_names"] = document_names

        base_query += """
            ORDER BY similarity DESC
            LIMIT :top_k;
        """

        sql_query = text(base_query)
        result = await db.execute(sql_query, query_params)
        rows = result.fetchall()

        if not rows:
            return []

        return rows

    except Exception as e:
        logger.error(f"Error retrieving documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving documents: {str(e)}")

async def query_llm_with_context(query: str, retrieved_chunks: list):
    """Query LLM with retrieved document context."""
    context_text = "\n".join([chunk[1] for chunk in retrieved_chunks])

    prompt = QA_TEMPLATE.format(context_str=context_text, query_str=query)

    try:
        llm_response = await llm_model.acomplete(prompt=prompt)
        return llm_response.text if hasattr(llm_response, "text") else llm_response
    except Exception as e:
        logger.error(f"LLM Query Failed: {str(e)}")
        raise HTTPException(status_code=500, detail="LLM failed to generate a response.")
