from contextlib import asynccontextmanager

from fastapi import FastAPI

from app_kit.ai.config import get_vector_db_settings
from app_kit.core.logger import logger
from app_kit.ai.vector_store.factory import vector_store_cache
from app_kit.ai.vector_store.registry import get_provider_cls


@asynccontextmanager
async def lifespan_vector_store_client(app: FastAPI):
    settings = get_vector_db_settings()
    logger.info(f"Initializing vector store client of kind: {settings.KIND}")
    provider = get_provider_cls(settings.KIND)
    client = provider.create_client(settings)
    if hasattr(app, "state"):
        app_kit.state.vector_store_client = client
    else:
        raise RuntimeError("FastAPI app does not have 'state' attribute.")
    logger.info("Vector store client initialized successfully.")

    yield

    # Cleanup on shutdown
    provider.close_client(client)
    # Clear the vector store cache
    vector_store_cache.clear()
