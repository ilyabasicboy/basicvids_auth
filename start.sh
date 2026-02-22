#!/bin/sh

# Set env and secret
if [ ! -f .env ]; then
    echo "SECRET_KEY=$(openssl rand -hex 32)" > .env
fi

# Run fastapi
exec uvicorn basicvids_auth.main:app --host 0.0.0.0 --port 8000 --reload