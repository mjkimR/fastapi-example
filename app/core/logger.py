import logging
from contextvars import ContextVar

request_id_var = ContextVar("request_id")


def get_request_id():
    return request_id_var.get()


def set_request_id(req_id: str):
    request_id_var.set(req_id)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
