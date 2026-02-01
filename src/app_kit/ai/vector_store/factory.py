from typing import Any

from cachetools import LRUCache
from langchain_core.vectorstores import VectorStore

import app_kit.core.vector_store.providers  # noqa: F401 to register providers
from app_kit.ai.config import get_vector_db_settings
from app_kit.ai.vector_store.registry import get_provider_cls

vector_store_cache = LRUCache(maxsize=16)


class VectorStoreFactory:
    def __init__(self, client: Any):
        self.client = client

    def get_vector_store(self, collection_name: str, model_name: str) -> VectorStore:
        """
        Returns a VectorStore implementation suitable for the client type.

        TODO: More detailed configuration (index settings, etc.) / multi vector search / ...
        """
        settings = get_vector_db_settings()
        cache_key = (settings.KIND, collection_name, model_name)
        if cache_key in vector_store_cache:
            return vector_store_cache[cache_key]
        provider = get_provider_cls(settings.KIND)
        store = provider.create_vector_store(self.client, collection_name, model_name)
        vector_store_cache[cache_key] = store
        return store
