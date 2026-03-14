#!/bin/bash
set -e

ENV_FILE=/basicvids_auth/data/.env

# Create .env and set Secret
if [ ! -f "$ENV_FILE" ]; then
    echo "Creating .env file..."
    SECRET_KEY=$(openssl rand -hex 32)
    echo "SECRET_KEY=$SECRET_KEY" > "$ENV_FILE"
fi

export $(grep -v '^#' "$ENV_FILE" | xargs)

# Calculate workers automatically
WORKERS=$(python -c "import multiprocessing; print(multiprocessing.cpu_count() * 2 + 1)")

echo "Starting server with $WORKERS workers"

exec gunicorn basicvids_auth.main:app \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --workers $WORKERS \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -