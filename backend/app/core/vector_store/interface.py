from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Any

from langchain_core.vectorstores import VectorStore

from app.core.config import VectorDBSettings


class VectorStoreProvider(ABC):
    @staticmethod
    @abstractmethod
    def create_client(config: VectorDBSettings) -> Any:
        """Create and return a vector store client based on the provided configuration."""
        pass

    @staticmethod
    @abstractmethod
    def close_client(client: Any) -> None:
        """Close the vector store client."""
        pass

    @staticmethod
    @abstractmethod
    def create_vector_store(client: Any, collection_name: str, model_name: str) -> VectorStore:
        """Create and return a VectorStore instance."""
        pass


@contextmanager
def import_error_handler(kind: str):
    """Context manager to handle import errors for vector store dependencies."""
    try:
        yield
    except ImportError as e:
        raise ImportError(
            f"Failed to import dependencies for vector store kind '{kind}'. Please install the required package."
        ) from e
