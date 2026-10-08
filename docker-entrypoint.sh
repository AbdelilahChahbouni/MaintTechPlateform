#!/bin/sh
set -e

# Ensure uploads directories exist inside container/volume
mkdir -p /app/uploads/cvs /app/uploads/avatars

# If AUTO_SEED is enabled, seed the database with Moroccan industrial talents
if [ "$AUTO_SEED" = "true" ] || [ "$AUTO_SEED" = "1" ]; then
    echo "[*] AUTO_SEED is enabled: Populating database with Moroccan maintenance technicians..."
    python seed.py || echo "[!] Seeding encountered a notice, proceeding..."
fi

# Dynamically set port if provided by cloud provider (e.g. Cloud Run, Render, Heroku)
PORT="${PORT:-5000}"

echo "[*] Launching MaintTech Jobs Maroc on 0.0.0.0:${PORT}..."

# If command is gunicorn, adjust port dynamically if PORT env var is customized
if [ "$1" = "gunicorn" ]; then
    exec gunicorn --workers="${GUNICORN_WORKERS:-4}" \
                  --threads="${GUNICORN_THREADS:-2}" \
                  --bind="0.0.0.0:${PORT}" \
                  --access-logfile="-" \
                  --error-logfile="-" \
                  "app:create_app()"
fi

# Otherwise execute passed custom command
exec "$@"
