from typing import Any

from app_kit.ai.models import AIModelFactory
from app_kit.ai.config import VectorDBSettings
from app_kit.ai.vector_store.interface import VectorStoreProvider, import_error_handler
from app_kit.ai.vector_store.registry import register_vector_store


@register_vector_store("qdrant")
class QdrantProvider(VectorStoreProvider):
    @staticmethod
    def create_client(settings: VectorDBSettings) -> Any:
        with import_error_handler("qdrant"):
            from qdrant_client import QdrantClient

        return QdrantClient(url=settings.URL, api_key=settings.API_KEY.get_secret_value() if settings.API_KEY else None)

    @staticmethod
    def close_client(client: Any) -> None:
        if client:
            client.close()

    @staticmethod
    def create_vector_store(client: Any, collection_name: str, model_name: str) -> Any:
        with import_error_handler("qdrant"):
            from langchain_qdrant import QdrantVectorStore
            from qdrant_client.http import models as conf
            from qdrant_client.http.exceptions import ApiException

        model_factory = AIModelFactory()
        # AIModelFactory internally caches embeddings
        embeddings = model_factory.get_embedding(model_name)

        if not client.collection_exists(collection_name=collection_name):
            dimension = model_factory.get_embedding_dimension(model_name)
            try:
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=conf.VectorParams(size=dimension, distance=conf.Distance.COSINE),
                )
            except ApiException as e:
                if "exists" in str(e):
                    pass
                else:
                    raise e

        return QdrantVectorStore(
            client=client,
            collection_name=collection_name,
            embedding=embeddings,
        )
