from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.responses import RedirectResponse
from app.router import router
from app.base.exceptions.handler import set_exception_handler
from app.core.logger import logger
from app.core.middlewares import (
    cors_middleware,
)
from app.core.middlewares import request_id_middleware


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
    app = FastAPI(
        title="ExampleApp",
        version="0.0.1",
        lifespan=lifespan,
        swagger_ui_parameters={
            "persistAuthorization": True,
            "docExpansion": "none",
            "filter": True,
        })

    @app.get("/")
    async def root():
        return RedirectResponse(url="/docs")

    request_id_middleware.add_middleware(app)
    cors_middleware.add_middleware(app)

    app.include_router(router)

    set_exception_handler(app)
    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(create_app(), host="localhost", port=7132)
