#!/bin/bash

# Simple build/run script for DigitalOcean droplet
# - Avoids /home/user/app; uses INSTALL_DIR=/opt/neuro-san-studio inside and outside the container
# - Uses dev/Dockerfile and dev/entrypoint_simple_dgo.sh

set -euo pipefail

VOLUME_NAME="neuro-san-studio-history"
IMAGE_NAME="neuro-san-dev"
CONTAINER_NAME="neuro-san-container"
DOCKERFILE_PATH="dev/Dockerfile"
INSTALL_DIR="${INSTALL_DIR:-/opt/neuro-san-studio}"
CONTAINER_APP_DIR="${CONTAINER_APP_DIR:-$INSTALL_DIR}"

# Ensure Docker volume exists
if docker volume inspect "$VOLUME_NAME" >/dev/null 2>&1; then
  echo "Volume $VOLUME_NAME exists."
else
  echo "Creating volume $VOLUME_NAME..."
  docker volume create "$VOLUME_NAME" >/dev/null
  echo "Volume $VOLUME_NAME created."
fi

# Build image
echo "Building Docker image $IMAGE_NAME..."
docker build -t "$IMAGE_NAME" -f "$DOCKERFILE_PATH" .
echo "Docker image $IMAGE_NAME built."

# Ensure install dir exists on host
sudo mkdir -p "$INSTALL_DIR"
if [ -n "${SUDO_USER:-}" ]; then
  sudo chown -R "$SUDO_USER":"$SUDO_USER" "$INSTALL_DIR"
else
  sudo chown -R "$USER":"$USER" "$INSTALL_DIR"
fi

# Run container with droplet entrypoint
echo "Running Docker container $CONTAINER_NAME (Droplet simple mode)..."
ENV_FILE_ARG=""
if [ -f .env ]; then
  ENV_FILE_ARG="--env-file .env"
fi

docker run -it $ENV_FILE_ARG --rm --name "$CONTAINER_NAME" \
  -p 4173:4173 \
  -p 30011:30011 \
  -p 8080:8080 \
  -p 5001:5001 \
  -v "$VOLUME_NAME:$CONTAINER_APP_DIR/.history" \
  -v "$(pwd):$CONTAINER_APP_DIR" \
  -w "$CONTAINER_APP_DIR" \
  --entrypoint bash \
  "$IMAGE_NAME" -c 'exec bash dev/entrypoint_simple_dgo.sh'

