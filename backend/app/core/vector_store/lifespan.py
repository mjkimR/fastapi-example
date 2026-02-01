from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_vector_db_settings
from app.core.logger import logger
from app.core.vector_store.factory import vector_store_cache
from app.core.vector_store.registry import get_provider_cls


@asynccontextmanager
async def lifespan_vector_store_client(app: FastAPI):
    settings = get_vector_db_settings()
    logger.info(f"Initializing vector store client of kind: {settings.KIND}")
    provider = get_provider_cls(settings.KIND)
    client = provider.create_client(settings)
    if hasattr(app, "state"):
        app.state.vector_store_client = client
    else:
        raise RuntimeError("FastAPI app does not have 'state' attribute.")
    logger.info("Vector store client initialized successfully.")

    yield

    # Cleanup on shutdown
    provider.close_client(client)
    # Clear the vector store cache
    vector_store_cache.clear()
