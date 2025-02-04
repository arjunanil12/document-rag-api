import pytest
import sys
import os
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.db.base import get_db, db_instance

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.fixture(scope="function")
async def setup_test_db():
    """✅ Ensure tables are created before running tests."""
    await db_instance.create_tables()  # ✅ Fix: Await this function properly

@pytest.fixture(scope="function")
async def test_db() -> AsyncSession:
    """Create a fresh async database session for each test."""
    async with db_instance.get_session() as session:
        yield session  # ✅ Returns actual AsyncSession
        await session.rollback()

@pytest.fixture(scope="module")
def client():
    """FastAPI Test Client for API testing."""
    return TestClient(app)