from fastapi import APIRouter, Depends, FastAPI
from app.llm.llm_initializer import LLMService
from app.embeddings.embedding_initializer import EmbeddingService
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.db.base import db_instance, get_db
from contextlib import asynccontextmanager

router = APIRouter()

# Define lifespan event
@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI Lifespan Event to manage startup and shutdown tasks."""
    # Initialize the database tables on app startup
    await db_instance.create_tables() 
    yield

# FastAPI app definition with lifespan
app = FastAPI(lifespan=lifespan)

# Include the router
app.include_router(router)

# FastAPI Health check route
@router.get("/")
def health_check():
    return {"status": "FastAPI server is running!"}

# Test database connection route
@router.get("/test_db")
async def test_database(db: AsyncSession = Depends(get_db)):
    """Test database connection asynchronously."""
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "Database connected successfully"}
    except Exception as e:
        return {"status": "Database connection failed", "error": str(e)}

# Test LLM route
@router.get("/test_llm")
async def test_llm():
    """Test Ollama LLM Initialization."""
    try:
        llm_instance = LLMService()
        response = await llm_instance.get_llm().acomplete("What is the capital of France?") 
        return {"status": "LLM Initialized", "response": response}
    except Exception as e:
        return {"status": "LLM Initialization failed", "error": str(e)}

# Test Embedding model route
@router.get("/test_embedding")
async def test_embedding():
    """Test Embedding Model."""
    try:
        embedding_instance = EmbeddingService()
        vector = await embedding_instance.get_embedding_model().aget_text_embedding("Hello, world!")
        return {"status": "Embedding Model Loaded", "vector_sample": vector[:5]} 
    except Exception as e:
        return {"status": "Embedding Model Initialization failed", "error": str(e)}
