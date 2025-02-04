from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
from app.utils.singleton import SingletonMeta
from app.config import settings

class EmbeddingService(metaclass=SingletonMeta):
    """Singleton for embedding model initialization using SingletonMeta."""

    def __init__(self):
        """Initialize the embedding model only once."""
        if not hasattr(self, "embedding_model"):
            self.embedding_model = HuggingFaceEmbedding(model_name=settings.EMBEDDING_MODEL)
            Settings.embed_model = self.embedding_model

    def get_embedding_model(self):
        """Return the embedding model instance."""
        return self.embedding_model