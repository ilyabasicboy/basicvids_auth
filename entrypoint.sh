#!/bin/bash
set -e

# path to data
ENV_FILE=/basicvids_auth/data/.env

# Create .env and set Secret
if [ ! -f "$ENV_FILE" ]; then
    echo "Creating .env file..."
    SECRET_KEY=$(openssl rand -hex 32)
    echo "SECRET_KEY=$SECRET_KEY" > "$ENV_FILE"
fi

export $(grep -v '^#' "$ENV_FILE" | xargs)

exec uvicorn basicvids_auth.main:app --host 0.0.0.0 --port 8000 --reload