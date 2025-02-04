import pytest
import json
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_query_retrieval(client: TestClient, test_db: AsyncSession):
    """Test the `/qna/retrieve` endpoint for successful retrieval of similar document chunks."""

    mock_retrieved_chunks = [
        ("Test Document 1", "This is a relevant chunk of text.", 0.95),
        ("Test Document 2", "Another relevant chunk.", 0.90),
        ("Test Document 3", "Yet another one.", 0.85),
    ]

    with patch("app.services.qna_service.retrieve_similar_chunks", new=AsyncMock(return_value=mock_retrieved_chunks)) as mock_chunks:
        assert mock_chunks.called is False
        response = client.get("/qna/retrieve", params={"query": "sample query", "top_k": 3})

    print("Mock Called:", mock_chunks.called)
    print("Response JSON:", response.json())

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
    assert data[0]["document_name"] == "Test Document 1"
    assert data[0]["chunk_text"] == "This is a relevant chunk of text."
    assert data[0]["similarity"] == 0.95


@pytest.mark.asyncio
async def test_query_retrieval_no_results(client: TestClient, test_db: AsyncSession):
    """Test the `/qna/retrieve` endpoint when no results are found."""

    with patch("app.services.qna_service.retrieve_similar_chunks", new=AsyncMock(return_value=[])) as mock_chunks:
        response = client.get("/qna/retrieve", params={"query": "unknown query", "top_k": 3})

    print("Mock Called:", mock_chunks.called)  # Debugging
    print("Response JSON:", response.json())   # Debugging

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_query_retrieval_exception(client: TestClient, test_db: AsyncSession):
    """Test `/qna/retrieve` API when an internal error occurs in `retrieve_similar_chunks`."""

    with patch("app.services.qna_service.retrieve_similar_chunks", new=AsyncMock(side_effect=Exception("DB Error"))) as mock_chunks:
        response = client.get("/qna/retrieve", params={"query": "error query", "top_k": 3})

    print("Mock Called:", mock_chunks.called)
    print("Response JSON:", response.json())

    assert response.status_code == 500
    assert "Error retrieving documents" in response.json()["detail"]


@pytest.mark.asyncio
async def test_query_answering(client: TestClient, test_db: AsyncSession):
    """Test the `/qna/query` endpoint where LLM successfully answers a query."""

    mock_retrieved_chunks = [
        ("Test Document", "Relevant context for answering the question.", 0.95)
    ]

    with patch("app.services.qna_service.retrieve_similar_chunks", new=AsyncMock(return_value=mock_retrieved_chunks)) as mock_chunks, \
         patch("app.services.qna_service.query_llm_with_context", new=AsyncMock(return_value="This is the answer.")) as mock_llm:

        response = client.get("/qna/query", params={"query": "What is the meaning of life?"})

    print("Mock Called:", mock_llm.called)
    print("Response JSON:", response.json())

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "What is the meaning of life?"
    assert data["answer"] == "This is the answer."


@pytest.mark.asyncio
async def test_query_answering_no_chunks(client: TestClient, test_db: AsyncSession):
    """Test the `/qna/query` endpoint when no relevant document chunks are retrieved."""

    with patch("app.services.qna_service.retrieve_similar_chunks", new=AsyncMock(return_value=[])) as mock_chunks, \
         patch("app.services.qna_service.query_llm_with_context", new=AsyncMock(return_value="No relevant information found.")) as mock_llm:

        response = client.get("/qna/query", params={"query": "Unknown question"})

    print("Mock Called:", mock_llm.called)
    print("Response JSON:", response.json())

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "Unknown question"
    assert data["answer"] == "No relevant information found."


@pytest.mark.asyncio
async def test_query_answering_llm_failure(client: TestClient, test_db: AsyncSession):
    """Test `/qna/query` API when the LLM fails to generate a response."""

    mock_retrieved_chunks = [
        ("Test Document", "Relevant context for answering the question.", 0.95)
    ]

    with patch("app.services.qna_service.retrieve_similar_chunks", new=AsyncMock(return_value=mock_retrieved_chunks)) as mock_chunks, \
         patch("app.services.qna_service.query_llm_with_context", new=AsyncMock(side_effect=Exception("LLM error"))) as mock_llm:

        response = client.get("/qna/query", params={"query": "complex query"})

    print("Mock Called:", mock_llm.called)
    print("Response JSON:", response.json())

    assert response.status_code == 500
    assert "LLM failed to generate a response" in response.json()["detail"]
