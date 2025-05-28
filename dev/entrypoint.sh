#!/usr/bin/env bash
set -euo pipefail

# entrypoint.sh: Initialization script for the Docker container
# 
# Environment detection strategy:
# 1. The host script (build_local.ps1 or build_local.sh) passes WINDOWS_ENV=true/false
# 2. Additionally, we perform a runtime network test to check if 0.0.0.0 connections work
# 3. If either detection method indicates Windows/WSL, we apply the necessary fixes
#
# This dual detection approach is more reliable than trying to detect the host OS
# from inside the container, which is inherently limited due to container isolation.

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

# Environment detection to handle 0.0.0.0 connection issues
# We'll use a simple approach that works regardless of OS:
# 1. Try to start a temporary server on 0.0.0.0
# 2. Try to access it from localhost
# 3. If it works, we don't need the proxy

# Function to check if we need the 0.0.0.0 fix
need_0000_fix() {
  echo "Testing if 0.0.0.0 connections work in this environment..."
  
  # Create a temporary file for a simple server
  cat > /tmp/test_server.py << 'EOF'
import http.server
import socketserver
import threading
import time
import urllib.request
import urllib.error

# Start a simple HTTP server on 0.0.0.0:8765
def run_server():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("0.0.0.0", 8765), handler) as httpd:
        print("Server started on 0.0.0.0:8765")
        httpd.handle_request()  # Handle just one request

# Start server in thread
server_thread = threading.Thread(target=run_server)
server_thread.daemon = True
server_thread.start()

# Give server time to start
time.sleep(1)

# Try to connect to the server using 0.0.0.0
try:
    urllib.request.urlopen("http://0.0.0.0:8765", timeout=2)
    print("SUCCESS: Connection to 0.0.0.0 works")
    exit(0)  # Success - no fix needed
except (urllib.error.URLError, ConnectionRefusedError) as e:
    print(f"FAILED: Cannot connect to 0.0.0.0: {e}")
    exit(1)  # Failure - fix needed
EOF

  # Run the test
  python /tmp/test_server.py &>/dev/null
  local result=$?
  rm /tmp/test_server.py
  
  # Return the result (0 = no fix needed, 1 = fix needed)
  return $result
}

# Set default for WINDOWS_ENV if not provided by the host script
WINDOWS_ENV=${WINDOWS_ENV:-false}

# Run the test
if need_0000_fix; then
  echo "Connection to 0.0.0.0 works correctly in this environment - no fixes needed"
  NEED_CONNECTION_FIX=false
else
  echo "Connection to 0.0.0.0 fails in this environment - will apply connection fixes"
  NEED_CONNECTION_FIX=true
  
  # If the network test indicates we need a fix, assume Windows/WSL environment
  # This provides a fallback detection method if WINDOWS_ENV wasn't explicitly set
  if [ "$WINDOWS_ENV" = "false" ]; then
    echo "Network test indicates Windows/WSL environment, overriding WINDOWS_ENV"
    WINDOWS_ENV=true
  fi
fi

# Show environment variables for debugging
echo "======= Environment Variables ======="
echo "NSFLOW_HOST: ${NSFLOW_HOST}"
echo "NSFLOW_PORT: ${NSFLOW_PORT}"
echo "VITE_API_HOST: ${VITE_API_HOST:-not set}"
echo "VITE_API_PORT: ${VITE_API_PORT:-not set}"
echo "Running in Windows/WSL environment: ${WINDOWS_ENV}"
echo "Need connection fix: ${NEED_CONNECTION_FIX}"
echo "======= End Environment Variables ======="

# Apply fixes based on both explicit Windows env flag AND connection test results
if [ "${WINDOWS_ENV}" = "true" ] || [ "${NEED_CONNECTION_FIX}" = "true" ]; then
  echo "Applying Windows/WSL specific fixes for 0.0.0.0 connections"
  
  # Override frontend connection variables
  export NSFLOW_FRONTEND_HOST=localhost
  export NSFLOW_CLIENT_HOST=localhost
  export NSFLOW_DEV_HOST=localhost
  export VITE_NSFLOW_HOST=localhost
  # Override any hardcoded 0.0.0.0 in the frontend code
  export FRONTEND_API_HOST=localhost
  
  # Check if we have Node.js and npm for the proxy
  if command -v node &>/dev/null && command -v npm &>/dev/null; then
    echo "Setting up proxy for 0.0.0.0 redirection..."
    
    # Create a simple NodeJS proxy server to intercept 0.0.0.0 requests and redirect them
    cat > /home/user/proxy.js << 'EOF'
const http = require('http');
const httpProxy = require('http-proxy');

// Create a proxy server
const proxy = httpProxy.createProxyServer({});

// Add error handling
proxy.on('error', (err, req, res) => {
  console.error('Proxy error:', err);
  res.writeHead(500, {
    'Content-Type': 'text/plain'
  });
  res.end('Proxy error');
});

// Create the server
const server = http.createServer((req, res) => {
  // Check if the request is trying to reach 0.0.0.0
  if (req.headers.host && req.headers.host.includes('0.0.0.0')) {
    console.log(`Redirecting request from ${req.headers.host} to localhost`);
    const target = req.headers.host.replace('0.0.0.0', 'localhost');
    req.headers.host = target;
    proxy.web(req, res, { target: `http://${target}` });
  } else {
    proxy.web(req, res, { target: 'http://localhost:30013' });
  }
});

console.log('Proxy server listening on port 8005');
server.listen(8005);
EOF

    # Check if http-proxy is installed
    if ! npm list -g http-proxy &>/dev/null; then
      echo "Installing http-proxy for the proxy server"
      npm install -g http-proxy || echo "Warning: Failed to install http-proxy, continuing without proxy"
    fi

    # Start the proxy server in the background
    echo "Starting proxy server for 0.0.0.0 redirection..."
    node /home/user/proxy.js &
  else
    echo "Node.js or npm not found - skipping proxy setup"
  fi
else
  echo "Running in standard Linux environment or 0.0.0.0 connections work correctly - no special fixes needed"
fi

# Run the main application
echo "Starting main application..."
python -m run
# 3) drop into interactive bash
exec /bin/bash -i