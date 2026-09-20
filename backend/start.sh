#!/bin/sh
set -e

echo "========================================"
echo "Running database migrations..."
echo "========================================"

python -m alembic upgrade head

echo "========================================"
echo "Starting data seeding in background..."
echo "========================================"

python -m app.db.seed &

echo "========================================"
echo "Starting FastAPI backend..."
echo "========================================"

exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload