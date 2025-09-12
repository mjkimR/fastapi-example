from http import HTTPStatus

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.core.exceptions.base import CustomException
from app.core.logger import logger, get_request_id


def set_exception_handler(app: FastAPI):
    @app.exception_handler(CustomException)
    async def exception_handler(_request: Request, exc: CustomException):
        logger.error(f"Error: {exc.log_message}", exc_info=exc.trace)

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "message": exc.message,
                "request_id": get_request_id(),
            }
        )

    @app.exception_handler(HTTPException)
    async def exception_handler(_request: Request, exc: HTTPException):
        logger.error(f"Error: {exc}", exc_info=True)

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "message": f"HTTPException with {exc.status_code}",
                "request_id": get_request_id(),
            }
        )

    @app.exception_handler(Exception)
    async def exception_handler(_request: Request, exc: Exception):
        logger.error(f"Unknown Error: {exc}", exc_info=exc)

        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content={
                "message": "Internal Server Error",
                "request_id": get_request_id()
            },
        )

    return app
