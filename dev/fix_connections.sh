#!/usr/bin/env bash
# fix_connections.sh: Script to fix connection issues on Windows/WSL

# Install required packages if not already installed
if ! command -v curl &>/dev/null || ! command -v netstat &>/dev/null; then
    echo "Installing required diagnostic tools..."
    apt-get update && apt-get install -y curl net-tools netcat iproute2
fi

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

# Create a function to test if a port is listening
port_is_listening() {
    netstat -tuln | grep -q ":$1 "
}

# Check for required services
echo "Checking for required services..."

echo -n "Frontend service (port 4173): "
if port_is_listening 4173; then
    echo "âœ“ Running"
else
    echo "âœ— Not running!"
fi

echo -n "Backend service (port 30013): "
if port_is_listening 30013; then
    echo "âœ“ Running"
else
    echo "âœ— Not running!"
fi

echo -n "Proxy service (port 8005): "
if port_is_listening 8005; then
    echo "âœ“ Running"
else
    echo "âœ— Not running"
    echo "Attempting to start proxy service..."
    
    # Check if proxy.js exists
    if [ -f /home/user/proxy.js ]; then
        echo "Found proxy.js, starting..."
        node /home/user/proxy.js &
        sleep 2
        if port_is_listening 8005; then
            echo "âœ“ Successfully started proxy service"
        else
            echo "âœ— Failed to start proxy service"
        fi
    else
        echo "âœ— proxy.js not found!"
    fi
fi

# Apply frontend fixups
if [ -d "/home/user/app/apps/conscious_assistant/static" ]; then
    echo "Applying frontend fixes..."
    
    # Create an advanced WebSocket fix JS file
    echo "Creating websocket_fix.js"
    cat > /home/user/app/apps/conscious_assistant/static/websocket_fix.js <<EOL
/**
 * websocket_fix.js - Advanced WebSocket and Socket.IO connectivity fixes
 * 
 * This script directly patches Socket.IO and native WebSocket implementations
 * to ensure proper connections even when the browser attempts to connect to 0.0.0.0
 */

(function() {
    console.log('Applying advanced WebSocket and Socket.IO fixes');
    
    // Store the original WebSocket constructor
    const OriginalWebSocket = window.WebSocket;
    
    // Patch the WebSocket constructor to redirect 0.0.0.0 to localhost
    window.WebSocket = function(url, protocols) {
        if (typeof url === 'string') {
            // Replace 0.0.0.0 with localhost in WebSocket URLs
            url = url.replace(/0\.0\.0\.0/g, 'localhost');
            console.log('⚙️ WebSocket connecting to:', url);
        }
        return new OriginalWebSocket(url, protocols);
    };
    
    // Copy over prototype and static properties
    Object.setPrototypeOf(window.WebSocket, OriginalWebSocket);
    window.WebSocket.prototype = OriginalWebSocket.prototype;
    window.WebSocket.CONNECTING = OriginalWebSocket.CONNECTING;
    window.WebSocket.OPEN = OriginalWebSocket.OPEN;
    window.WebSocket.CLOSING = OriginalWebSocket.CLOSING;
    window.WebSocket.CLOSED = OriginalWebSocket.CLOSED;
    
    // Wait for Socket.IO to be loaded
    function patchSocketIO() {
        if (window.io) {
            const originalConnect = window.io.connect || window.io;
            
            // Override the connect function
            const patchedConnect = function(url, options) {
                if (typeof url === 'string' && url.includes('0.0.0.0')) {
                    url = url.replace(/0\.0\.0\.0/g, 'localhost');
                    console.log('⚙️ Socket.IO connecting to:', url);
                }
                return originalConnect(url, options);
            };
            
            // Apply the patched version
            if (window.io.connect) {
                window.io.connect = patchedConnect;
            } else {
                window.io = patchedConnect;
            }
            
            console.log('✅ Successfully patched Socket.IO');
        } else {
            console.log('⏳ Waiting for Socket.IO to be loaded...');
            setTimeout(patchSocketIO, 100);
        }
    }
    
    // Apply Socket.IO patches
    patchSocketIO();
    
    // Patch the location.hostname if it's 0.0.0.0
    if (window.location.hostname === '0.0.0.0') {
        try {
            Object.defineProperty(window.location, 'hostname', {
                get: function() { return 'localhost'; }
            });
            console.log('✅ Patched location.hostname to return localhost');
        } catch (e) {
            console.warn('❌ Failed to patch location.hostname:', e);
        }
    }
    
    // Patch document.domain
    if (document.domain === '0.0.0.0') {
        try {
            document.domain = 'localhost';
            console.log('✅ Set document.domain to localhost');
        } catch (e) {
            console.warn('❌ Failed to set document.domain:', e);
        }
    }
    
    console.log('✅ Advanced WebSocket and Socket.IO fixes applied');
})();
EOL
    
    # Create the regular connection fix JS file
    echo "Creating connection_fix.js"
    cat > /home/user/app/apps/conscious_assistant/static/connection_fix.js <<EOL
// Fix for Windows/WSL environments - auto-injected by fix_connections.sh
(function() {
    console.log('Applying connection fixes for Windows/WSL environments');
    
    // Replace any uses of 0.0.0.0 with localhost
    var originalFetch = window.fetch;
    window.fetch = function(url, options) {
        if (typeof url === 'string' && url.includes('0.0.0.0')) {
            url = url.replace('0.0.0.0', 'localhost');
            console.log('Redirecting fetch from 0.0.0.0 to localhost:', url);
        }
        return originalFetch.call(this, url, options);
    };
    
    // Replace any uses of 0.0.0.0 in XMLHttpRequest
    var originalOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(method, url, async, user, password) {
        if (typeof url === 'string' && url.includes('0.0.0.0')) {
            url = url.replace('0.0.0.0', 'localhost');
            console.log('Redirecting XHR from 0.0.0.0 to localhost:', url);
        }
        return originalOpen.call(this, method, url, async, user, password);
    };
    
    // Fix WebSocket connections
    var originalWebSocket = window.WebSocket;
    window.WebSocket = function(url, protocols) {
        if (typeof url === 'string' && url.includes('0.0.0.0')) {
            url = url.replace(/0\.0\.0\.0/g, 'localhost');
            console.log('Redirecting WebSocket from 0.0.0.0 to localhost:', url);
        }
        return new originalWebSocket(url, protocols);
    };
    
    // Fix EventSource connections (for SSE)
    var originalEventSource = window.EventSource;
    if (originalEventSource) {
        window.EventSource = function(url, options) {
            if (typeof url === 'string' && url.includes('0.0.0.0')) {
                url = url.replace(/0\.0\.0\.0/g, 'localhost');
                console.log('Redirecting EventSource from 0.0.0.0 to localhost:', url);
            }
            return new originalEventSource(url, options);
        };
    }
    
    console.log('Enhanced connection fixes applied successfully');
})();
EOL

    echo "Creating enhanced override_config.js..."
    cat > /home/user/app/apps/conscious_assistant/static/override_config.js << EOL
// Enhanced override configuration for Windows/WSL compatibility
window.FORCE_LOCALHOST = true;
window.API_HOST = 'localhost';
window.API_PORT = '30013';
window.FRONTEND_PORT = location.port || '4173';
window.WS_PROTOCOL = 'ws';
window.API_PROTOCOL = 'http';

// Define API URLs for consistent usage across the app
window.API_BASE_URL = window.API_PROTOCOL + '://' + window.API_HOST + ':' + window.API_PORT;
window.WS_BASE_URL = window.WS_PROTOCOL + '://' + window.API_HOST + ':' + window.API_PORT;

// Fix document.domain if it's set to 0.0.0.0
if (document.domain === '0.0.0.0') {
    try {
        document.domain = 'localhost';
    } catch (e) {
        console.warn('Could not set document.domain to localhost:', e);
    }
}

console.log('Enhanced override config loaded with the following settings:');
console.log('- API Base URL:', window.API_BASE_URL);
console.log('- WebSocket Base URL:', window.WS_BASE_URL);
console.log('- Document domain:', document.domain);
EOL
    
    echo "âœ“ Created connection fix script"
    
    # Verify it exists
    if [ -f "/home/user/app/apps/conscious_assistant/static/connection_fix.js" ]; then
        echo "âœ“ Frontend fixes applied successfully"
    else
        echo "âœ— Failed to create frontend fixes"
    fi
else
    echo "âœ— Frontend static directory not found!"
fi

echo "Connection fixes complete. Please restart your browser and try accessing the application again."
echo "If issues persist, please run the 'network_debug.sh' script for more detailed diagnostics."
