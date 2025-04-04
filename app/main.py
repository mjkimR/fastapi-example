from contextlib import asynccontextmanager
from http import HTTPStatus

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.responses import RedirectResponse
from api import router


def get_lifespan():
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        print("Starting app lifespan")
        yield
        print("End of app lifespan")

    return lifespan


def create_app():
    """Create the FastAPI app and include the router."""
    lifespan = get_lifespan()
    app = FastAPI(title="ExampleApp", version="0.0.1", lifespan=lifespan)

    @app.get("/")
    async def root():
        return RedirectResponse(url="/docs")

    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    @app.exception_handler(Exception)
    async def exception_handler(_request: Request, exc: Exception):
        if isinstance(exc, HTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={"message": str(exc.detail)},
            )
        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content={"message": str(exc)},
        )

    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(create_app(), host="0.0.0.0", port=8000)
