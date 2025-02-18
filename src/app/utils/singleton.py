import threading

class SingletonMeta(type):
    """Thread-safe Singleton metaclass."""
    
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        """Ensure only one instance is created."""
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
