from http import HTTPStatus

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.base.exceptions.base import CustomException
from app.core.logger import logger


def set_exception_handler(app: FastAPI):
    @app.exception_handler(CustomException)
    async def custom_exception_handler(_request: Request, exc: CustomException):
        if exc.trace:
            logger.exception(f"Error: {exc.log_message}")
        else:
            logger.error(f"Error: {exc.log_message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "message": exc.message,
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_request: Request, exc: HTTPException):
        logger.exception(f"Error: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "message": exc.detail,
            },
        )

    @app.exception_handler(NotImplementedError)
    async def not_implemented_exception_handler(
        _request: Request, exc: NotImplementedError
    ):
        return JSONResponse(
            status_code=HTTPStatus.NOT_IMPLEMENTED,
            content={
                "message": "The requested functionality is not implemented.",
            },
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(_request: Request, exc: ValueError):
        logger.exception(f"ValueError: {exc}")
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content={
                "message": "Invalid input provided.",
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(_request: Request, exc: Exception):
        logger.exception(f"Unknown Error: {exc}")
        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content={
                "message": "Internal Server Error",
            },
        )

    return app
