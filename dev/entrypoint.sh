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
# If not explicitly set, try to determine it from the container
WINDOWS_ENV=${WINDOWS_ENV:-false}

# Always run the test regardless of the WINDOWS_ENV value
# This is more reliable than any OS detection
echo "Testing if 0.0.0.0 connections work in this container..."
if need_0000_fix; then
  echo "Connection to 0.0.0.0 works correctly in this environment - no fixes needed"
  NEED_CONNECTION_FIX=false
else
  echo "Connection to 0.0.0.0 fails in this environment - will apply connection fixes"
  NEED_CONNECTION_FIX=true
  
  # If the network test indicates we need a fix, always set WINDOWS_ENV to true
  # This ensures we apply all necessary fixes
  WINDOWS_ENV=true
  echo "Network test indicates connection issues - will apply Windows/WSL fixes"
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
  export VITE_API_HOST=localhost
  # Override any hardcoded 0.0.0.0 in the frontend code
  export FRONTEND_API_HOST=localhost
  
  # Create a script that will patch the frontend JavaScript files at runtime
  # to replace all occurrences of 0.0.0.0 with localhost
  echo "Creating JavaScript patcher script..."
  cat > /home/user/patch_frontend.sh << 'EOF'
#!/bin/bash
# Script to find and patch JavaScript files with 0.0.0.0 references

JS_DIR="apps/conscious_assistant/static"
if [ ! -d "$JS_DIR" ]; then
  echo "JavaScript directory not found at $JS_DIR"
  exit 1
fi

echo "Patching JavaScript files to replace 0.0.0.0 with localhost..."

# Find all JS files
FOUND_FILES=$(find "$JS_DIR" -name "*.js")

# Replace 0.0.0.0 with localhost in all JS files
for file in $FOUND_FILES; do
  echo "Checking $file"
  if grep -q "0.0.0.0" "$file"; then
    echo "Patching $file (found 0.0.0.0 references)"
    cp "$file" "${file}.bak"  # Create backup
    sed -i 's/0.0.0.0/localhost/g' "$file"
    echo "✅ Patched $file"
  fi
done

echo "Patching complete!"
EOF

  chmod +x /home/user/patch_frontend.sh
  
  # Check if we have Node.js and npm for the proxy
  if command -v node &>/dev/null && command -v npm &>/dev/null; then
    echo "Setting up proxy for 0.0.0.0 redirection..."
    
    # Create a more comprehensive NodeJS proxy server to intercept 0.0.0.0 requests and redirect them
    cat > /home/user/proxy.js << 'EOF'
const http = require('http');
const httpProxy = require('http-proxy');

// Create a proxy server that can handle both HTTP and WebSocket
const proxy = httpProxy.createProxyServer({
  ws: true,  // Enable WebSocket support
  xfwd: true, // Forward X-Forwarded headers
  changeOrigin: true, // Change the origin of the host header
  autoRewrite: true // Rewrite the location headers
});

// Add error handling
proxy.on('error', (err, req, res) => {
  console.error('Proxy error:', err);
  if (res && res.writeHead) {
    res.writeHead(500, {
      'Content-Type': 'text/plain'
    });
    res.end(`Proxy error: ${err.message}`);
  }
});

// Helper to determine target based on host header and URL
function determineTarget(req) {
  console.log(`Determining target for request: ${req.method} ${req.url}, Host: ${req.headers.host || 'unknown'}`);
  
  // Extract host and port from the Host header
  let targetHost = 'localhost';
  let targetPort = '4173'; // Default to frontend port
  let protocol = 'http';
  
  if (req.headers.host) {
    const hostParts = req.headers.host.split(':');
    // Always replace 0.0.0.0 with localhost
    targetHost = hostParts[0] === '0.0.0.0' ? 'localhost' : hostParts[0];
    if (hostParts.length > 1) {
      targetPort = hostParts[1];
    }
  }
  
  // Override based on the URL path
  if (req.url) {
    if (req.url.includes('/api/v1')) {
      // API requests should go to the server port
      targetPort = '30013';
    }
    
    // Check for WebSocket protocol
    if (req.headers.upgrade && req.headers.upgrade.toLowerCase() === 'websocket') {
      protocol = 'ws';
    }
  }
  
  return { 
    host: targetHost, 
    port: targetPort, 
    protocol: protocol,
    url: `${protocol}://${targetHost}:${targetPort}`
  };
}

// Create the server
const server = http.createServer((req, res) => {
  // Log all incoming requests for debugging
  console.log(`[PROXY] Received request: ${req.method} ${req.url}, Host: ${req.headers.host || 'unknown'}`);
  
  const target = determineTarget(req);
  
  // Always modify the host header to use localhost
  if (req.headers.host && req.headers.host.includes('0.0.0.0')) {
    console.log(`[PROXY] Replacing 0.0.0.0 with localhost in host header`);
    req.headers.host = req.headers.host.replace('0.0.0.0', 'localhost');
  }
  
  console.log(`[PROXY] Forwarding to ${target.url}`);
  proxy.web(req, res, { target: target.url });
});

// Handle WebSocket upgrade
server.on('upgrade', (req, socket, head) => {
  console.log(`[PROXY] WebSocket upgrade request: ${req.url}, Host: ${req.headers.host || 'unknown'}`);
  
  const target = determineTarget(req);
  target.protocol = 'ws'; // Ensure WebSocket protocol
  const wsUrl = `${target.protocol}://${target.host}:${target.port}`;
  
  // Always modify the host header to use localhost
  if (req.headers.host && req.headers.host.includes('0.0.0.0')) {
    console.log(`[PROXY] Replacing 0.0.0.0 with localhost in WebSocket host header`);
    req.headers.host = req.headers.host.replace('0.0.0.0', 'localhost');
  }
  
  console.log(`[PROXY] Forwarding WebSocket to ${wsUrl}`);
  proxy.ws(req, socket, head, { target: wsUrl });
});

// Add host to accept connections from any interface
console.log('Proxy server listening on 0.0.0.0:8005');
server.listen(8005, '0.0.0.0', () => {
  console.log('[PROXY] Server is running and ready to redirect traffic');
  console.log('[PROXY] Handling connections from:');
  console.log('       - http://0.0.0.0:8005  (container internal)');
  console.log('       - http://localhost:8005 (browser access)');
});
EOF

    # Install http-proxy locally for the proxy server
    echo "Installing http-proxy for the proxy server"
    cd /home/user
    npm init -y
    npm install http-proxy --save
    
    # Start the proxy server in the background
    echo "Starting proxy server for 0.0.0.0 redirection..."
    node /home/user/proxy.js &
    
    # Verify that the proxy server is running
    sleep 2
    if pgrep -f "node /home/user/proxy.js" > /dev/null; then
      echo "✅ Proxy server is running successfully"
    else
      echo "❌ ERROR: Proxy server failed to start - Windows/WSL connections may fail"
      echo "   This might be because Node.js or npm installation failed."
      echo "   Try rebuilding the container or manually starting the proxy with:"
      echo "   node /home/user/proxy.js"
    fi
    
    # Return to app directory
    cd /home/user/app
  else
    echo "Node.js or npm not found - skipping proxy setup"
  fi
else
  echo "Running in standard Linux environment or 0.0.0.0 connections work correctly - no special fixes needed"
fi

# Run basic connectivity tests
echo "Running basic connectivity tests..."
echo "Testing connection to localhost:4173..."
curl -s -o /dev/null -w "%{http_code}" http://localhost:4173 || echo "Failed to connect to localhost:4173"
echo "Testing connection to localhost:30013..."
curl -s -o /dev/null -w "%{http_code}" http://localhost:30013 || echo "Failed to connect to localhost:30013"

echo "Testing network interfaces..."
ip addr show || echo "Failed to show network interfaces"

# Print helper script information
echo ""
echo "===== Helper Scripts Available ====="
echo "If you encounter connection issues, you can use these helper scripts:"
echo "  /home/user/app/dev/network_debug.sh - Diagnose network connectivity issues"
echo "  /home/user/app/dev/fix_connections.sh - Apply additional fixes for Windows/WSL environments"
echo "=============================="
echo ""

# Apply patch to frontend files if in Windows/WSL environment
if [ "${WINDOWS_ENV}" = "true" ] || [ "${NEED_CONNECTION_FIX}" = "true" ]; then
  echo "Patching frontend JavaScript files to replace 0.0.0.0 with localhost..."
  /home/user/patch_frontend.sh
  
  # Create a special global frontend variable override file
  cat > /home/user/app/apps/conscious_assistant/static/override_config.js << EOF
// Override configuration - automatically generated
window.FORCE_LOCALHOST = true;
window.API_HOST = 'localhost';
console.log('Loading override config to force localhost connections');
EOF
  
  echo "Frontend patching complete!"
fi

# Since we can't chmod scripts in the mounted directory on Windows, 
# provide instructions to run them with bash directly
echo "==================================================================================="
echo "  🛠️  Helper Tools Available  🛠️"
echo "==================================================================================="
echo "If you experience any connectivity issues, you can use these diagnostic tools:"
echo "  - bash /home/user/app/dev/network_debug.sh - Check network connections and service status"
echo "  - bash /home/user/app/dev/fix_connections.sh - Apply additional fixes for browser connectivity"
echo "  - sudo bash /home/user/app/dev/host_fix.sh - Fix host resolution issues (requires sudo)"
echo ""
echo "Common Browser Connection Issues:"
echo "  - If you see 'Connection failed' or 'Failed to fetch' in the UI, try:"
echo "    1. Open browser developer tools (F12) and look at Console errors"
echo "    2. If errors show 0.0.0.0 connections, run fix_connections.sh"
echo "    3. Access the app using http://localhost:4173 instead of 0.0.0.0"
echo "==================================================================================="

# Run the main application
echo "Starting main application..."
python -m run
# 3) drop into interactive bash
exec /bin/bash -i