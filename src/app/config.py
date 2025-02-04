from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# Get the root directory (where .env is located)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    LLM_MODEL: str = "llama3.1:8b"
    LLM_TIMEOUT: float = 120.0

    OLLAMA_HOST: str = "localhost"
    OLLAMA_PORT: int = 11434

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Explicitly tell Pydantic where the .env file is
    model_config = SettingsConfigDict(env_file=str(ROOT_DIR / ".env"), env_file_encoding="utf-8")

settings = Settings()
