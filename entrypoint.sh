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

REFRESH_TOKEN_CLEANUP_CRON=${REFRESH_TOKEN_CLEANUP_CRON:-"17 * * * *"}
CRON_FILE=/etc/cron.d/basicvids_auth
CRON_LOG=/var/log/basicvids_auth_cron.log

echo "Configuring refresh token cleanup cron: $REFRESH_TOKEN_CLEANUP_CRON"
touch "$CRON_LOG"
cat > "$CRON_FILE" <<EOF
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
PYTHONUNBUFFERED=1
$REFRESH_TOKEN_CLEANUP_CRON root cd /basicvids_auth && /usr/local/bin/python -m basicvids_auth.commands.delete_expired_refresh_tokens >> $CRON_LOG 2>&1
EOF
chmod 0644 "$CRON_FILE"
crontab "$CRON_FILE"
service cron start

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
