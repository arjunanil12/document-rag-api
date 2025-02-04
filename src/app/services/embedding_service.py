import asyncio
from pypdf import PdfReader
from app.embeddings.embedding_initializer import EmbeddingService
from llama_index.core.node_parser import TokenTextSplitter

# Initialize Embedding Model Singleton
embedding_instance = EmbeddingService()
embedding_model = embedding_instance.get_embedding_model()

async def extract_text_from_pdf(file) -> str:
    """Extract text from a PDF asynchronously using a thread executor."""
    loop = asyncio.get_running_loop()
    # Use run_in_executor to run blocking PDF text extraction outside of the async event loop
    return await loop.run_in_executor(None, lambda: "\n".join([ 
        page.extract_text() or "" for page in PdfReader(file.file).pages 
    ]).strip())

async def generate_embeddings(chunks: list[str]) -> list:
    """Generate embeddings asynchronously for all document chunks."""
    # Gather embeddings for all chunks concurrently
    return await asyncio.gather(*[embedding_model.aget_text_embedding(chunk) for chunk in chunks])

async def chunk_and_generate_embeddings(extracted_text: str):
    """Chunk the extracted text and generate embeddings asynchronously."""
    # Initialize the text splitter for chunking the extracted text
    text_splitter = TokenTextSplitter(chunk_size=512, chunk_overlap=50)
    chunks = text_splitter.split_text(extracted_text)
    # Generate embeddings concurrently for all chunks
    chunk_embeddings = await generate_embeddings(chunks)
    return chunks, chunk_embeddings
