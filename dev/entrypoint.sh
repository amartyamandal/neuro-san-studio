#!/usr/bin/env bash
# Remove strict error handling that causes container to exit
# set -euo pipefail

# entrypoint.sh: Simple initialization script for the Docker container

# Print hello message
echo "hello from entrypoint"

# 0) fix up PATH so ~/.local/bin (where --user installs land) is found
export PATH="$HOME/.local/bin:$PATH"

# move into the app directory
cd /home/user/app

# 2) print a greeting
echo "hello from entrypoint, let's install requirements and run the app"
python -m pip install -r requirements.txt
python -m pip install -r requirements-build.txt

# Start the application as a background daemon
echo "Starting NeuroSan server as background daemon..."
nohup python -m run > /tmp/neuroSan.log 2>&1 &
SERVER_PID=$!
echo $SERVER_PID > /tmp/neuroSan.pid

# Give the server a moment to start
sleep 3
echo "NeuroSan server started as daemon (PID: $SERVER_PID)"
echo "Logs: tail -f /tmp/neuroSan.log"
echo "Stop: kill \$(cat /tmp/neuroSan.pid) or use 'stop_server' command"

# Create helper functions for server management
cat > /tmp/server_control.sh << 'EOF'
#!/bin/bash

# Debug function to show what's happening
debug_info() {
    echo "Debug: PID file exists: $([ -f /tmp/neuroSan.pid ] && echo 'yes' || echo 'no')"
    if [ -f /tmp/neuroSan.pid ]; then
        echo "Debug: PID file content: $(cat /tmp/neuroSan.pid)"
        echo "Debug: Process check: $(kill -0 $(cat /tmp/neuroSan.pid) 2>/dev/null && echo 'running' || echo 'not running')"
    fi
}

start_server() {
    if [ -f /tmp/neuroSan.pid ] && kill -0 $(cat /tmp/neuroSan.pid) 2>/dev/null; then
        echo "NeuroSan server is already running (PID: $(cat /tmp/neuroSan.pid))"
    else
        echo "Starting NeuroSan server..."
        cd /home/user/app
        nohup python -m run > /tmp/neuroSan.log 2>&1 &
        echo $! > /tmp/neuroSan.pid
        sleep 2
        echo "NeuroSan server started (PID: $(cat /tmp/neuroSan.pid))"
    fi
}

stop_server() {
    echo "Attempting to stop server..."
    debug_info
    
    if [ -f /tmp/neuroSan.pid ]; then
        PID=$(cat /tmp/neuroSan.pid)
        echo "Found PID file with PID: $PID"
        
        if kill -0 $PID 2>/dev/null; then
            echo "Process $PID is running. Stopping..."
            if kill $PID 2>/dev/null; then
                echo "Kill signal sent successfully"
                sleep 1
                if kill -0 $PID 2>/dev/null; then
                    echo "Process still running, sending SIGTERM..."
                    kill -TERM $PID 2>/dev/null
                    sleep 2
                fi
                rm -f /tmp/neuroSan.pid
                echo "NeuroSan server stopped"
            else
                echo "Failed to send kill signal to PID $PID"
            fi
        else
            echo "Process $PID is not running (stale PID file)"
            rm -f /tmp/neuroSan.pid
        fi
    else
        echo "No PID file found - server may not be running"
    fi
}

server_status() {
    debug_info
    
    if [ -f /tmp/neuroSan.pid ]; then
        PID=$(cat /tmp/neuroSan.pid)
        if kill -0 $PID 2>/dev/null; then
            echo "NeuroSan server is running (PID: $PID)"
            echo "Logs: tail -f /tmp/neuroSan.log"
        else
            echo "NeuroSan server is not running (stale PID file)"
            rm -f /tmp/neuroSan.pid
        fi
    else
        echo "NeuroSan server is not running"
    fi
}

show_logs() {
    if [ -f /tmp/neuroSan.log ]; then
        echo "Showing NeuroSan logs (Ctrl+C to exit):"
        tail -f /tmp/neuroSan.log
    else
        echo "No log file found at /tmp/neuroSan.log"
    fi
}
EOF

chmod +x /tmp/server_control.sh

# Source the functions directly into current shell
source /tmp/server_control.sh

# Create simple command wrappers that definitely work
cat > /tmp/server_commands.sh << 'CMD_EOF'
#!/bin/bash
# Simple command wrappers that always work

start() {
    source /tmp/server_control.sh
    start_server
}

stop() {
    source /tmp/server_control.sh  
    stop_server
}

status() {
    source /tmp/server_control.sh
    server_status
}

logs() {
    source /tmp/server_control.sh
    show_logs
}

restart() {
    source /tmp/server_control.sh
    stop_server
    sleep 3
    start_server
}
CMD_EOF

chmod +x /tmp/server_commands.sh
source /tmp/server_commands.sh

# Export all functions (ignore any errors)
export -f start_server 2>/dev/null || true
export -f stop_server 2>/dev/null || true
export -f server_status 2>/dev/null || true  
export -f show_logs 2>/dev/null || true
export -f start 2>/dev/null || true
export -f stop 2>/dev/null || true
export -f status 2>/dev/null || true
export -f logs 2>/dev/null || true
export -f restart 2>/dev/null || true

# Add to bashrc (ignore errors)
{
    echo ""
    echo "# Server control functions"
    echo "alias start_server='source /tmp/server_control.sh && start_server'"
    echo "alias stop_server='source /tmp/server_control.sh && stop_server'"
    echo "alias server_status='source /tmp/server_control.sh && server_status'"
    echo "alias show_logs='source /tmp/server_control.sh && show_logs'"
    echo "alias start='source /tmp/server_commands.sh && start'"
    echo "alias stop='source /tmp/server_commands.sh && stop'"
    echo "alias status='source /tmp/server_commands.sh && status'" 
    echo "alias logs='source /tmp/server_commands.sh && logs'"
    echo "alias restart='source /tmp/server_commands.sh && restart'"
} >> ~/.bashrc 2>/dev/null || true

echo ""
echo "🚀 Server Control Commands Available:"
echo ""
echo "  SIMPLE COMMANDS (recommended):"
echo "    start    - Start the NeuroSan server"
echo "    stop     - Stop the NeuroSan server"  
echo "    restart  - Restart the NeuroSan server"
echo "    status   - Check server status"
echo "    logs     - View server logs (tail -f)"
echo ""
echo "  FULL COMMANDS (alternative):"
echo "    start_server   - Start the NeuroSan server"
echo "    stop_server    - Stop the NeuroSan server"
echo "    server_status  - Check server status"
echo "    show_logs      - View server logs"
echo ""
echo "  DIRECT COMMANDS (fallback):"
echo "    kill \$(cat /tmp/neuroSan.pid)  - Direct kill"
echo "    tail -f /tmp/neuroSan.log       - Direct logs"
echo "    source /tmp/server_control.sh && stop_server  - Manual stop"
echo ""
echo "Try the simple commands first: start, stop, status, logs"
echo ""

# 3) drop into interactive bash
exec /bin/bash -i