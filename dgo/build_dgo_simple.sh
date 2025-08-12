#!/bin/bash

# Simple build/run script for DigitalOcean droplet
set -euo pipefail

IMAGE_NAME="neuro-san"
CONTAINER_NAME="neuro-san-container"
DOCKERFILE_PATH="dgo/Dockerfile"

# Build image
echo "Building Docker image $IMAGE_NAME..."
docker build -t "$IMAGE_NAME" -f "$DOCKERFILE_PATH" .
echo "Docker image $IMAGE_NAME built."

# Remove any existing container with the same name
docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true

# Run container
echo "Running Docker container $CONTAINER_NAME..."
docker run -d --name "$CONTAINER_NAME" \
  -p 4173:4173 \
  -p 5003:5003 \
  -p 8080:8080 \
  -p 30013:30013 \
  "$IMAGE_NAME"

