#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint_dgo] Starting DigitalOcean entrypoint"

# Resolve app directory
APP_DIR="${CONTAINER_APP_DIR:-/app}"
cd "$APP_DIR" || { echo "[FATAL] Cannot cd to $APP_DIR"; exit 1; }

# Source .env if available
if [ -f "$APP_DIR/.env" ]; then
  if [ -r "$APP_DIR/.env" ]; then
    set -a
    . "$APP_DIR/.env" || echo "[entrypoint_dgo][WARN] Failed to source .env (non-fatal)"
    set +a
    echo "[entrypoint_dgo] Sourced .env"
  else
    echo "[entrypoint_dgo][WARN] .env exists but is not readable; skipping"
  fi
fi

# Start the application
echo "[entrypoint_dgo] Starting NeuroSan services..."
exec python run.py
