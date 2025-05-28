#!/usr/bin/env bash
# network_debug.sh - A helper script to debug connection issues in the container

set -euo pipefail

# Check if we're running inside Docker (multiple detection methods)
if [ -f /.dockerenv ] || grep -q docker /proc/1/cgroup || grep -q container /proc/1/cgroup || grep -q lxc /proc/1/cgroup; then
    echo "âœ“ Running inside Docker container"
else
    # One more check - check for certain container-specific paths
    if [ -d /home/user/app ] && [ "$(whoami)" = "user" ]; then
        echo "âœ“ Running inside neuro-san container (detected by paths)"
    else
        echo "âš ï¸ This script is designed to run inside the Docker container."
        echo "Please run it from inside the neuro-san-container."
        exit 1
    fi
fi

echo "===== NeuroSan Studio Network Diagnostics ====="
echo "This script helps diagnose connection issues between the host and container"

echo -e "\n1. Container Network Interfaces:"
ip addr show

echo -e "\n2. Container Listening Ports:"
netstat -tuln

echo -e "\n3. Testing Services:"
echo "- Testing connection to frontend on port 4173:"
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:4173 || echo "Failed to connect to frontend"

echo "- Testing connection to API on port 30013:"
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:30013 || echo "Failed to connect to API"

echo "- Testing connection to proxy on port 8005:"
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8005 || echo "Failed to connect to proxy"

echo -e "\n4. Testing if 0.0.0.0 connections work:"
# Create a temporary file for a simple server
cat > /tmp/test_server.py << 'EOF'
import http.server
import socketserver
import threading
import time
import urllib.request
import urllib.error
import socket
import random

# Find an available port
def find_available_port():
    for port in range(8765, 8865):  # Try ports in range 8765-8864
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(("0.0.0.0", port))
            s.close()
            return port
        except OSError:
            continue
    return random.randint(10000, 65000)  # Last resort: try a random port

# Start a simple HTTP server on 0.0.0.0 with an available port
def run_server():
    global server_port
    server_port = find_available_port()
    handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("0.0.0.0", server_port), handler) as httpd:
            print(f"Server started on 0.0.0.0:{server_port}")
            httpd.handle_request()  # Handle just one request
    except OSError as e:
        print(f"Server error: {e}")
        exit(1)

# Global variable to store the port
server_port = None

# Start server in thread
server_thread = threading.Thread(target=run_server)
server_thread.daemon = True
server_thread.start()

# Give server time to start
time.sleep(2)

# Try to connect to the server using 0.0.0.0
if server_port:
    try:
        urllib.request.urlopen(f"http://0.0.0.0:{server_port}", timeout=2)
        print(f"SUCCESS: Connection to 0.0.0.0:{server_port} works")
        exit(0)  # Success - no fix needed
    except (urllib.error.URLError, ConnectionRefusedError) as e:
        print(f"FAILED: Cannot connect to 0.0.0.0:{server_port}: {e}")
        exit(1)  # Failure - fix needed
else:
    print("FAILED: Could not start test server")
    exit(1)
EOF

# Run the test
python /tmp/test_server.py
result=$?
rm /tmp/test_server.py

if [ $result -eq 0 ]; then
  echo "âœ… 0.0.0.0 connections work correctly!"
else
  echo "âŒ 0.0.0.0 connections fail - this may be causing your issues"
fi

echo -e "\n5. Environment Variables:"
echo "NSFLOW_HOST: ${NSFLOW_HOST:-not set}"
echo "NSFLOW_PORT: ${NSFLOW_PORT:-not set}"
echo "VITE_API_HOST: ${VITE_API_HOST:-not set}"
echo "VITE_API_PORT: ${VITE_API_PORT:-not set}" 
echo "VITE_API_PROTOCOL: ${VITE_API_PROTOCOL:-not set}"
echo "VITE_WS_PROTOCOL: ${VITE_WS_PROTOCOL:-not set}"
echo "WINDOWS_ENV: ${WINDOWS_ENV:-not set}"

echo -e "\n===== End of Diagnostics ====="
echo "If you're experiencing connection issues:"
echo "1. Make sure ports 4173, 30013, and 8005 are published to the host"
echo "2. Try accessing the services via localhost instead of 0.0.0.0"
echo "3. Check if the proxy server is running with: ps aux | grep proxy.js"
