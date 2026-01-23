from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.responses import RedirectResponse
from app.api import router
from app.core.exceptions.handler import set_exception_handler
from app.core.logger import logger
from app.core.middlewares import (
    static_middleware,
    cors_middleware,
    request_id_middleware,
)


def get_lifespan():
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("Starting app lifespan")
        yield
        logger.info("End of app lifespan")

    return lifespan


def create_app():
    """Create the FastAPI app and include the router."""
    lifespan = get_lifespan()
    app = FastAPI(title="ExampleApp", version="0.0.1", lifespan=lifespan)

    @app.get("/")
    async def root():
        return RedirectResponse(url="/docs")

    # Add middlewares in order (request ID should be first)
    request_id_middleware.add_middleware(app)
    cors_middleware.add_middleware(app)
    static_middleware.add_middleware(app)

    app.include_router(router)

    set_exception_handler(app)
    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(create_app(), host="localhost", port=8851)
