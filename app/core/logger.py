import os.path
from pathlib import Path

import sys
from contextvars import ContextVar
from loguru import logger

# Request ID context variable
request_id_var = ContextVar("request_id", default=None)


def get_request_id():
    """Get the current request ID from context"""
    return request_id_var.get()


def set_request_id(req_id: str):
    """Set the request ID in context"""
    request_id_var.set(req_id)


def format_record(record):
    """Custom formatter that includes request ID"""
    request_id = get_request_id()
    if request_id:
        record["extra"]["request_id"] = request_id
    else:
        record["extra"]["request_id"] = "N/A"
    return record


# Remove default handler
logger.remove()

# Add console handler with custom format
logger.add(
    sys.stdout,
    format="[<yellow>{extra[request_id]}</yellow>] <green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
    level="INFO",
    filter=format_record,
    colorize=True,
    backtrace=False,
    diagnose=False,
)

# Add file handler
logger.add(
    os.path.join(Path(__file__).parent.parent.parent, "logs/app.log"),
    format="[{extra[request_id]}] {time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} | {message}",
    level="INFO",
    filter=format_record,
    rotation="1 day",
    retention="30 days",
    compression="zip",
    backtrace=False,
    diagnose=False,
)
