import logging
from fastapi import FastAPI
from app.routes import ingestion, qna, test

# Configure the logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

# Include route handlers
app.include_router(test.router, tags=["Test"])
app.include_router(ingestion.router, tags=["Ingestion"])
app.include_router(qna.router, prefix="/qna", tags=["QnA"])

# Log application startup
logger.info("FastAPI is running with debugging enabled.")
