from abc import ABC, abstractmethod
from typing import Any


class CacheProvider(ABC):
    @abstractmethod
    def set(self, key: str, value: Any, expire_seconds: int = None):
        pass
        
    @abstractmethod
    def get(self, key: str) -> Any | None:
        pass
        
    @abstractmethod
    def delete(self, key: str):
        pass

class InMemoryCacheProvider(CacheProvider):
    """
    Fallback cache provider. 
    RedisCacheProvider will implement this interface in the future.
    """
    def __init__(self):
        self._cache = {}
        
    def set(self, key: str, value: Any, expire_seconds: int = None):
        # Time expiration not fully mocked for simplicity
        self._cache[key] = value
        
    def get(self, key: str) -> Any | None:
        return self._cache.get(key)
        
    def delete(self, key: str):
        if key in self._cache:
            del self._cache[key]
