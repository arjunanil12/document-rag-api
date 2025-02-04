from llama_index.llms.ollama import Ollama
from app.utils.singleton import SingletonMeta
from app.config import settings

class LLMService(metaclass=SingletonMeta):
    """Singleton for LLM initialization using SingletonMeta."""
    
    def __init__(self):
        """Initialize the LLM model only once."""
        if not hasattr(self, "llm"):
            self.llm = Ollama(model=settings.LLM_MODEL, request_timeout=settings.LLM_TIMEOUT)

    def get_llm(self):
        """Return the LLM instance."""
        return self.llm