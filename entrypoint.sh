#!/bin/bash
set -e

# path to data
ENV_FILE=/basicvids_auth/data/.env
PORT=${APP_PORT:-8000}

# Create .env and set Secret
if [ ! -f "$ENV_FILE" ]; then
    echo "Creating .env file..."
    SECRET_KEY=$(openssl rand -hex 32)
    echo "SECRET_KEY=$SECRET_KEY" > "$ENV_FILE"
fi

export $(grep -v '^#' "$ENV_FILE" | xargs)

exec gunicorn basicvids_auth.main:app \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:$PORT \
    --workers 4 \
    --timeout 120