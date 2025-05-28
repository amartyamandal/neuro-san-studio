#!/bin/bash
# host_fix.sh: Script to fix localhost vs 0.0.0.0 issues in the container
# This script directly modifies the /etc/hosts file inside the container

echo "Checking for host connectivity issues..."

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "⚠️ This script needs to run as root. Please use:"
    echo "    sudo bash host_fix.sh"
    exit 1
fi

# Check if we're running inside Docker
if [ ! -f /.dockerenv ] && ! grep -q docker /proc/1/cgroup && ! grep -q container /proc/1/cgroup; then
    echo "⚠️ This script should only be run inside the Docker container."
    exit 1
fi

# Backup the hosts file
cp /etc/hosts /etc/hosts.bak

# Check if 0.0.0.0 is already in /etc/hosts
if grep -q "0.0.0.0" /etc/hosts; then
    echo "✅ 0.0.0.0 is already defined in /etc/hosts"
else
    echo "Adding 0.0.0.0 to /etc/hosts..."
    echo "0.0.0.0 localhost" >> /etc/hosts
fi

# Check if 0.0.0.0 resolves to the localhost IP
echo -n "Testing if 0.0.0.0 resolves correctly... "
if ping -c 1 -W 1 0.0.0.0 >/dev/null 2>&1; then
    echo "✅ 0.0.0.0 resolves to a valid IP"
else
    echo "❌ 0.0.0.0 does not resolve correctly"
fi

# Ensure localhost resolves to 127.0.0.1
echo -n "Testing if localhost resolves correctly... "
if ping -c 1 -W 1 localhost >/dev/null 2>&1; then
    echo "✅ localhost resolves to a valid IP"
else
    echo "❌ localhost does not resolve correctly"
    echo "Adding localhost to /etc/hosts..."
    echo "127.0.0.1 localhost" >> /etc/hosts
fi

# Run basic connection tests
echo "Running basic connection tests..."
echo -n "Testing connection to localhost:4173... "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:4173 2>/dev/null; then
    echo "✅ Success"
else
    echo "❌ Failed"
fi

echo -n "Testing connection to 0.0.0.0:4173... "
if curl -s -o /dev/null -w "%{http_code}" http://0.0.0.0:4173 2>/dev/null; then
    echo "✅ Success"
else
    echo "❌ Failed"
fi

echo -n "Testing connection to localhost:30013... "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:30013 2>/dev/null; then
    echo "✅ Success"
else
    echo "❌ Failed"
fi

echo -n "Testing connection to 0.0.0.0:30013... "
if curl -s -o /dev/null -w "%{http_code}" http://0.0.0.0:30013 2>/dev/null; then
    echo "✅ Success"
else
    echo "❌ Failed"
fi

# Try to fix the issue with a proxy if needed
if ! curl -s -o /dev/null http://0.0.0.0:4173 2>/dev/null && curl -s -o /dev/null http://localhost:4173 2>/dev/null; then
    echo "⚠️ Detected a common issue: 0.0.0.0 connections fail but localhost works"
    echo "This is a known issue on Windows/WSL environments."
    
    echo "Starting the 0.0.0.0 to localhost proxy service..."
    bash /home/user/app/dev/fix_connections.sh
    
    echo "Please try accessing the application again using localhost in your browser."
fi

echo "Connection check and fixes completed."
echo "If you're still experiencing issues, please run: bash /home/user/app/dev/network_debug.sh"
