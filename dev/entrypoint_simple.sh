#!/usr/bin/env bash

# Simple, robust entrypoint that won't exit on errors
echo "hello from entrypoint"

# Fix PATH
export PATH="$HOME/.local/bin:$PATH"

# Move to app directory
cd /home/user/app || exit 1

# Install requirements (with error handling)
echo "Installing requirements..."
python -m pip install -r requirements.txt || echo "Warning: Failed to install requirements.txt"
python -m pip install -r requirements-build.txt || echo "Warning: Failed to install requirements-build.txt"

# Start the server
echo "Starting NeuroSan server..."
nohup python -m run > /tmp/neuroSan.log 2>&1 &
SERVER_PID=$!
echo $SERVER_PID > /tmp/neuroSan.pid
sleep 3

echo "NeuroSan server started (PID: $SERVER_PID)"
echo ""
echo "=== SERVER CONTROL ==="
echo "To stop server: kill \$(cat /tmp/neuroSan.pid)"
echo "To view logs:   tail -f /tmp/neuroSan.log"
echo "To check PID:   cat /tmp/neuroSan.pid"
echo ""

# Create a simple stop script
cat > /tmp/stop_server.sh << 'EOF'
#!/bin/bash
if [ -f /tmp/neuroSan.pid ]; then
    PID=$(cat /tmp/neuroSan.pid)
    echo "Stopping server PID: $PID"
    kill $PID 2>/dev/null && echo "Server stopped" || echo "Kill failed"
    rm -f /tmp/neuroSan.pid
else
    echo "No PID file found"
fi
EOF

chmod +x /tmp/stop_server.sh

# Create simple start script
cat > /tmp/start_server.sh << 'EOF'
#!/bin/bash
if [ -f /tmp/neuroSan.pid ]; then
    PID=$(cat /tmp/neuroSan.pid)
    if kill -0 $PID 2>/dev/null; then
        echo "Server is already running (PID: $PID)"
        exit 0
    else
        echo "Removing stale PID file"
        rm -f /tmp/neuroSan.pid
    fi
fi

echo "Starting NeuroSan server..."
cd /home/user/app
nohup python -m run > /tmp/neuroSan.log 2>&1 &
NEW_PID=$!
echo $NEW_PID > /tmp/neuroSan.pid
sleep 2

if kill -0 $NEW_PID 2>/dev/null; then
    echo "Server started successfully (PID: $NEW_PID)"
else
    echo "Failed to start server"
    rm -f /tmp/neuroSan.pid
fi
EOF

chmod +x /tmp/start_server.sh

# Create simple restart script
cat > /tmp/restart_server.sh << 'EOF'
#!/bin/bash
echo "Restarting NeuroSan server..."

# Stop if running
if [ -f /tmp/neuroSan.pid ]; then
    PID=$(cat /tmp/neuroSan.pid)
    if kill -0 $PID 2>/dev/null; then
        echo "Stopping existing server (PID: $PID)"
        kill $PID 2>/dev/null
        sleep 3
    fi
    rm -f /tmp/neuroSan.pid
fi

# Start fresh
echo "Starting server..."
cd /home/user/app
nohup python -m run > /tmp/neuroSan.log 2>&1 &
NEW_PID=$!
echo $NEW_PID > /tmp/neuroSan.pid
sleep 2

if kill -0 $NEW_PID 2>/dev/null; then
    echo "Server restarted successfully (PID: $NEW_PID)"
else
    echo "Failed to restart server"
    rm -f /tmp/neuroSan.pid
fi
EOF

chmod +x /tmp/restart_server.sh

# Create simple status script
cat > /tmp/server_status.sh << 'EOF'
#!/bin/bash
if [ -f /tmp/neuroSan.pid ]; then
    PID=$(cat /tmp/neuroSan.pid)
    if kill -0 $PID 2>/dev/null; then
        echo "Server is running (PID: $PID)"
    else
        echo "Server is not running (stale PID)"
        rm -f /tmp/neuroSan.pid
    fi
else
    echo "Server is not running"
fi
EOF

chmod +x /tmp/server_status.sh

echo "Simple commands created:"
echo "  /tmp/start_server.sh   - Start the server"
echo "  /tmp/stop_server.sh    - Stop the server"
echo "  /tmp/restart_server.sh - Restart the server"
echo "  /tmp/server_status.sh  - Check server status"
echo ""
echo "Quick commands:"
echo "  kill \$(cat /tmp/neuroSan.pid)  - Direct kill"
echo "  tail -f /tmp/neuroSan.log       - View logs"
echo ""

# Create simple function wrappers for convenience
# First clean up any existing aliases that might conflict
cat > ~/.bashrc_clean << 'CLEAN_EOF'
# Clean bashrc for NeuroSan
export PATH="$HOME/.local/bin:$PATH"

# Simple server control functions
start() { /tmp/start_server.sh; }
stop() { /tmp/stop_server.sh; }
restart() { /tmp/restart_server.sh; }
status() { /tmp/server_status.sh; }
logs() { tail -f /tmp/neuroSan.log; }

CLEAN_EOF

# Replace the bashrc to avoid conflicts
mv ~/.bashrc ~/.bashrc_backup 2>/dev/null || true
mv ~/.bashrc_clean ~/.bashrc

# Define functions in current session too
start() { /tmp/start_server.sh; }
stop() { /tmp/stop_server.sh; }
restart() { /tmp/restart_server.sh; }
status() { /tmp/server_status.sh; }
logs() { tail -f /tmp/neuroSan.log; }

echo "Convenient functions available:"
echo "  start    - Start the server"
echo "  stop     - Stop the server" 
echo "  restart  - Restart the server"
echo "  status   - Check server status"
echo "  logs     - View logs (Ctrl+C to exit)"
echo ""
echo "These should work immediately in your shell!"
echo ""

# Start interactive bash (this should not exit)
echo "Starting interactive shell..."
exec /bin/bash --login
