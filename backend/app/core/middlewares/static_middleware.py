from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import get_repo_path


def add_middleware(app: FastAPI):
    app.mount("/static", StaticFiles(directory=f"{get_repo_path()}/backend/app/static"), name="static")
