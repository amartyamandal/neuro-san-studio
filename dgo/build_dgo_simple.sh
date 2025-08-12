#!/bin/bash

# Simple build/run script for DigitalOcean droplet
set -euo pipefail

IMAGE_NAME="neuro-san"
CONTAINER_NAME="neuro-san-container"
DOCKERFILE_PATH="dgo/Dockerfile"

# Build image
echo "Building Docker image $IMAGE_NAME..."
docker build --no-cache -t "$IMAGE_NAME" -f "$DOCKERFILE_PATH" .
echo "Docker image $IMAGE_NAME built."

# Remove any existing container with the same name
docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true

# Prepare env-file arg if .env exists
ENV_FILE_ARG=""
if [ -f .env ]; then
  ENV_FILE_ARG="--env-file .env"
fi

# Run container
echo "Running Docker container $CONTAINER_NAME..."
docker run -d --name "$CONTAINER_NAME" $ENV_FILE_ARG \
  -p 4173:4173 \
  -p 5001:5001 \
  -p 8080:8080 \
  -p 30011:30011 \
  "$IMAGE_NAME"

