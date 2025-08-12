#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint_dgo] Starting DigitalOcean entrypoint"

# Resolve app directory: prefer env var, else current dir, else DO install path
APP_DIR="${CONTAINER_APP_DIR:-${PWD:-/opt/neuro-san-studio}}"
cd "$APP_DIR" || { echo "[FATAL] Cannot cd to $APP_DIR"; exit 1; }

# PATH tweaks
export PATH="$HOME/.local/bin:$PATH"

# Create and activate a virtual environment to avoid system package conflicts
VENV_DIR="$APP_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
  echo "[entrypoint_dgo] Creating venv at $VENV_DIR"
  python -m venv "$VENV_DIR"
fi
# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"
echo "[entrypoint_dgo] Using Python: $(python -V)"
echo "[entrypoint_dgo] Using Pip: $(pip -V)"

# Force-correct NeuroSan/NSFlow connectivity (override any bad values from .env)
export NEURO_SAN_CONNECTION_TYPE="grpc"
export NEURO_SAN_SERVER_HOST="127.0.0.1"
export NEURO_SAN_SERVER_PORT="30011"
echo "[entrypoint_dgo] NS config => ${NEURO_SAN_CONNECTION_TYPE}://${NEURO_SAN_SERVER_HOST}:${NEURO_SAN_SERVER_PORT}"

# Ensure logs (and TTS cache) exist and are writable
mkdir -p "$APP_DIR/logs" "$APP_DIR/logs/tts_cache" || true
chmod -R 777 "$APP_DIR/logs" || true

echo "[entrypoint_dgo] Upgrading pip/setuptools/wheel..."
python -m pip install --no-cache-dir --upgrade pip setuptools wheel || true

echo "[entrypoint_dgo] Installing requirements (with retry)..."
set +e
attempt=0
max_attempts=2
until [ $attempt -ge $max_attempts ]
do
  attempt=$((attempt+1))
  echo "[entrypoint_dgo] pip install -r requirements.txt (attempt $attempt/$max_attempts)"
  python -m pip install --no-cache-dir -r requirements.txt && break
  echo "[entrypoint_dgo][WARN] requirements.txt install failed (attempt $attempt)"
  sleep 3
done

# Optional build-time requirements, non-fatal
python -m pip install --no-cache-dir -r requirements-build.txt || echo "[WARN] Failed to install requirements-build.txt"

# Verify critical deps; if missing, try minimal fallback set and re-check (in venv)
python - <<'PY'
import sys
missing = []
for m in ("flask","flask_socketio","eventlet","neuro_san"):
    try:
        __import__(m)
    except Exception:
        missing.append(m)
if missing:
    print("__MISSING__", ",".join(missing))
else:
    print("__MISSING__")
PY
MISSING=$(tail -n 1 /tmp/neuroSan.log 2>/dev/null | sed -n 's/^__MISSING__\s*//p')
# The above won't work because we executed a separate python; capture properly instead:
MISSING=$(python - <<'PY'
import sys
missing = []
for m in ("flask","flask_socketio","eventlet","neuro_san"):
    try:
        __import__(m)
    except Exception:
        missing.append(m)
print(",".join(missing))
PY
)
if [ -n "$MISSING" ]; then
  echo "[entrypoint_dgo][WARN] Missing modules: $MISSING; installing minimal fallback set..."
  python -m pip install --no-cache-dir Flask flask-socketio eventlet openai pyhocon python-dotenv uvicorn fastapi nsflow neuro-san neuro-san-web-client || true
  # Re-check critical imports; if still missing, abort start so user can inspect
  MISSING2=$(python - <<'PY'
import sys
missing = []
for m in ("flask","flask_socketio","eventlet","neuro_san"):
    try:
        __import__(m)
    except Exception:
        missing.append(m)
print(",".join(missing))
PY
)
  if [ -n "$MISSING2" ]; then
    echo "[entrypoint_dgo][FATAL] Still missing modules after fallback: $MISSING2"
    exit 1
  fi
fi
set -e

# Start NeuroSan server
echo "[entrypoint_dgo] Starting NeuroSan server..."
nohup python -m run > /tmp/neuroSan.log 2>&1 &
NS_PID=$!
echo $NS_PID > /tmp/neuroSan.pid
sleep 2
if kill -0 "$NS_PID" 2>/dev/null; then
  echo "[entrypoint_dgo] NeuroSan server started (PID: $NS_PID)"
else
  echo "[entrypoint_dgo][WARN] NeuroSan failed to start. See /tmp/neuroSan.log"
fi

# Start CRUSE Flask UI (port 5001)
echo "[entrypoint_dgo] Starting CRUSE UI (port 5001)..."
nohup python -m apps.cruse.interface_flask > /tmp/cruse.log 2>&1 &
CRUSE_PID=$!
echo $CRUSE_PID > /tmp/cruse.pid
sleep 2
if kill -0 "$CRUSE_PID" 2>/dev/null; then
  echo "[entrypoint_dgo] CRUSE started (PID: $CRUSE_PID)"
else
  echo "[entrypoint_dgo][WARN] CRUSE failed to start. See /tmp/cruse.log"
fi

# Start NSFlow FastAPI backend (port 4173)
echo "[entrypoint_dgo] Starting NSFlow backend (port 4173)..."
nohup python -m uvicorn nsflow.backend.main:app --host 0.0.0.0 --port 4173 > "$APP_DIR/logs/nsflow.log" 2>&1 &
NSFLOW_PID=$!
echo $NSFLOW_PID > /tmp/nsflow.pid
sleep 2
if kill -0 "$NSFLOW_PID" 2>/dev/null; then
  echo "[entrypoint_dgo] NSFlow started (PID: $NSFLOW_PID)"
else
  echo "[entrypoint_dgo][WARN] NSFlow failed to start. See $APP_DIR/logs/nsflow.log"
fi

# If NSFlow backend (FastAPI on 4173) is present, set its runtime config to our NS settings
(
  for i in {1..30}; do
    if curl -fsS http://127.0.0.1:4173/api/v1/ping >/dev/null 2>&1; then
      echo "[entrypoint_dgo] Detected NSFlow backend; setting runtime config..."
      curl -fsS -X POST http://127.0.0.1:4173/api/v1/set_ns_config \
        -H 'Content-Type: application/json' \
        -d "{\"NEURO_SAN_CONNECTION_TYPE\":\"grpc\",\"NEURO_SAN_SERVER_HOST\":\"127.0.0.1\",\"NEURO_SAN_SERVER_PORT\":30011}" \
        && echo "[entrypoint_dgo] NSFlow config set." \
        || echo "[entrypoint_dgo][WARN] Failed to set NSFlow config."
      # Show the applied config
      curl -fsS http://127.0.0.1:4173/api/v1/get_ns_config || true
      break
    fi
    sleep 2
  done
) &

# Helper scripts
cat > /tmp/start_server.sh << 'EOF'
#!/bin/bash
APP_DIR="${CONTAINER_APP_DIR:-${PWD:-/opt/neuro-san-studio}}"
if [ -f "$APP_DIR/.venv/bin/activate" ]; then . "$APP_DIR/.venv/bin/activate"; fi
if [ -f /tmp/neuroSan.pid ]; then
  PID=$(cat /tmp/neuroSan.pid)
  if kill -0 $PID 2>/dev/null; then echo "Server already running (PID: $PID)"; exit 0; else rm -f /tmp/neuroSan.pid; fi
fi
cd "$APP_DIR" || exit 1
nohup python -m run > /tmp/neuroSan.log 2>&1 &
NEW_PID=$!
echo $NEW_PID > /tmp/neuroSan.pid
sleep 1
kill -0 $NEW_PID 2>/dev/null && echo "Server started (PID: $NEW_PID)" || { echo "Failed to start"; rm -f /tmp/neuroSan.pid; }
EOF
chmod +x /tmp/start_server.sh

cat > /tmp/stop_server.sh << 'EOF'
#!/bin/bash
if [ -f /tmp/neuroSan.pid ]; then
  PID=$(cat /tmp/neuroSan.pid)
  kill $PID 2>/dev/null || true
  sleep 1
  if kill -0 $PID 2>/dev/null; then echo "Kill failed"; else echo "Server stopped"; fi
  rm -f /tmp/neuroSan.pid
else
  echo "No server PID file"
fi
EOF
chmod +x /tmp/stop_server.sh

cat > /tmp/restart_server.sh << 'EOF'
#!/bin/bash
/tmp/stop_server.sh
/tmp/start_server.sh
EOF
chmod +x /tmp/restart_server.sh

cat > /tmp/server_status.sh << 'EOF'
#!/bin/bash
if [ -f /tmp/neuroSan.pid ]; then
  PID=$(cat /tmp/neuroSan.pid)
  if kill -0 $PID 2>/dev/null; then echo "Server running (PID: $PID)"; else echo "Server not running (stale PID)"; rm -f /tmp/neuroSan.pid; fi
else
  echo "Server not running"
fi
EOF
chmod +x /tmp/server_status.sh

cat > /tmp/cruse_start.sh << 'EOF'
#!/bin/bash
APP_DIR="${CONTAINER_APP_DIR:-${PWD:-/opt/neuro-san-studio}}"
if [ -f "$APP_DIR/.venv/bin/activate" ]; then . "$APP_DIR/.venv/bin/activate"; fi
if [ -f /tmp/cruse.pid ]; then
  PID=$(cat /tmp/cruse.pid)
  if kill -0 $PID 2>/dev/null; then echo "CRUSE already running (PID: $PID)"; exit 0; else rm -f /tmp/cruse.pid; fi
fi
cd "$APP_DIR" || exit 1
nohup python -m apps.cruse.interface_flask > /tmp/cruse.log 2>&1 &
NEWPID=$!
echo $NEWPID > /tmp/cruse.pid
sleep 1
kill -0 $NEWPID 2>/dev/null && echo "CRUSE started (PID: $NEWPID)" || { echo "Failed to start CRUSE"; rm -f /tmp/cruse.pid; }
EOF
chmod +x /tmp/cruse_start.sh

cat > /tmp/cruse_stop.sh << 'EOF'
#!/bin/bash
if [ -f /tmp/cruse.pid ]; then
  PID=$(cat /tmp/cruse.pid)
  kill $PID 2>/dev/null || true
  sleep 1
  if kill -0 $PID 2>/dev/null; then echo "Kill failed"; else echo "CRUSE stopped"; fi
  rm -f /tmp/cruse.pid
else
  echo "No CRUSE PID file"
fi
EOF
chmod +x /tmp/cruse_stop.sh

cat > /tmp/cruse_restart.sh << 'EOF'
#!/bin/bash
/tmp/cruse_stop.sh
/tmp/cruse_start.sh
EOF
chmod +x /tmp/cruse_restart.sh

cat > /tmp/cruse_status.sh << 'EOF'
#!/bin/bash
if [ -f /tmp/cruse.pid ]; then
  PID=$(cat /tmp/cruse.pid)
  if kill -0 $PID 2>/dev/null; then echo "CRUSE running (PID: $PID)"; else echo "CRUSE not running (stale PID)"; rm -f /tmp/cruse.pid; fi
else
  echo "CRUSE not running"
fi
EOF
chmod +x /tmp/cruse_status.sh

# Quick help
cat <<EON
[entrypoint_dgo] Ready. Useful commands inside container:
  tail -f /tmp/neuroSan.log
  tail -f /tmp/cruse.log
  /tmp/server_status.sh
  /tmp/cruse_status.sh
  /tmp/restart_server.sh
  /tmp/cruse_restart.sh
EON

# Do not exec a shell here; the docker run wrapper appends 'sleep infinity'
exit 0
