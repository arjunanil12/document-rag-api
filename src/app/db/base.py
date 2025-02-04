from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.sql import text
from app.utils.singleton import SingletonMeta
from app.config import settings
from app.db.models import Base

class Database(metaclass=SingletonMeta):
    """Singleton for database connection using Async SQLAlchemy."""

    def __init__(self):
        """Initialize database only once."""
        if not hasattr(self, "engine"):
            self.engine = create_async_engine(
                f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
                f"{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}",
                echo=False,
            )
            self.SessionLocal = async_sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)

    async def get_session(self) -> AsyncSession:
        """Return a new async database session."""
        async with self.SessionLocal() as session:
            yield session

    async def enable_pgvector(self):
        """Enable pgvector extension in PostgreSQL."""
        async with self.engine.begin() as connection:
            try:
                await connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                print("✅ pgvector extension enabled!")
            except ProgrammingError as e:
                print(f"⚠️ Error enabling pgvector: {e}")

    async def create_tables(self):
        """Create all tables in the database if they don't exist."""
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

# Singleton Database Instance
db_instance = Database()

async def get_db():
    """FastAPI Dependency to get an async database session."""
    async for session in db_instance.get_session():
        try:
            yield session
        finally:
            await session.close()


