#!/usr/bin/env bash
set -euo pipefail

# Stop and remove container
docker rm -f neuro-san-container || true

# Remove image(s)
docker rmi -f neuro-san-dev || true
docker image prune -f || true

# Remove volume (persists user data; only do this if you want a fresh start)
docker volume rm neuro-san-studio-history || true

# Remove ufw rules (only if you want to clean firewall entries)
ufw delete allow 4173/tcp || true
ufw delete allow 5001/tcp || true
ufw delete allow 8080/tcp || true
ufw delete allow 30011/tcp || true

# Remove install directory
rm -rf /opt/neuro-san-studio
