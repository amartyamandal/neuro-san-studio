#!/usr/bin/env bash
# Expose localhost-bound services to the droplet's public interface using socat.
# Useful when apps listen on 127.0.0.1 but you want public access on the same port.

set -euo pipefail

PORTS=(4173 5003 8080 30013)

require_root() {
  if [ "$(id -u)" -ne 0 ]; then
    echo "[expose] Please run as root: sudo $0" >&2
    exit 1
  fi
}

ensure_socat() {
  if ! command -v socat >/dev/null 2>&1; then
    echo "[expose] Installing socat..."
    apt-get update -y >/dev/null 2>&1 || true
    apt-get install -y socat >/dev/null 2>&1
  fi
}

open_firewall() {
  if command -v ufw >/dev/null 2>&1; then
    for p in "${PORTS[@]}"; do
      ufw allow "$p"/tcp >/dev/null 2>&1 || true
    done
  fi
}

start_forwarder() {
  local port="$1"
  # If something already listens on 0.0.0.0:$port, skip
  if ss -ltn '( sport = :'"$port"' )' | grep -q 'LISTEN'; then
    echo "[expose] Port $port already listening; skipping."
    return 0
  fi
  # Launch a background socat forwarder from 0.0.0.0:$port -> 127.0.0.1:$port
  nohup socat TCP-LISTEN:"$port",fork,reuseaddr,bind=0.0.0.0 TCP:127.0.0.1:"$port" \
    >/var/log/socat_$port.log 2>&1 &
  echo $! > "/var/run/socat_$port.pid"
  sleep 0.2
  if ss -ltn '( sport = :'"$port"' )' | grep -q 'LISTEN'; then
    echo "[expose] Forwarding 0.0.0.0:$port -> 127.0.0.1:$port (PID $(cat /var/run/socat_$port.pid))"
  else
    echo "[expose][WARN] Failed to start forwarder for $port. Check /var/log/socat_$port.log"
  fi
}

main() {
  require_root
  ensure_socat
  open_firewall
  for p in "${PORTS[@]}"; do
    start_forwarder "$p"
  done
}

main "$@"
