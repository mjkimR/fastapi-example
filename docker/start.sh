#!/bin/bash

set -e

alembic upgrade head
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:create_app --bind "0.0.0.0:7132"