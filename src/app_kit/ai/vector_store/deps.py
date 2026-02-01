from typing import Annotated, Any

from fastapi import Depends, Request
from langchain_core.vectorstores import VectorStore

from app_kit.ai.vector_store.factory import VectorStoreFactory


def get_vector_store_client(request: Request) -> Any:
    """
    Returns the vector store client instance.
    The return type may vary depending on KIND.
    """
    return request.app_kit.state.vector_store_client


def get_vector_store_factory(client: Annotated[Any, Depends(get_vector_store_client)]) -> VectorStoreFactory:
    """
    Dependency injection for FastAPI.

    Useful when collection name and embedding model name are dynamic.
    """
    return VectorStoreFactory(client)


def get_vector_store_dependency(collection_name: str, model_name: str):
    """
    Returns a FastAPI dependency for injecting a VectorStore.

    Example:
        Depends(get_vector_store_dependency("my_collection", "openai-embedding"))
    """

    def dependency(factory: Annotated[VectorStoreFactory, Depends(get_vector_store_factory)]) -> VectorStore:
        return factory.get_vector_store(collection_name, model_name)

    return dependency
