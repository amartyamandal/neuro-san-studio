#!/bin/bash

# Script to clean up the Docker container and image for NeuroSan
set -euo pipefail

CONTAINER_NAME="neuro-san-container"
IMAGE_NAME="neuro-san"

# Stop and remove the container if it exists
echo "Stopping and removing container $CONTAINER_NAME if it exists..."
docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || echo "No container to remove."

# Remove the Docker image if it exists
echo "Removing Docker image $IMAGE_NAME if it exists..."
docker rmi "$IMAGE_NAME" >/dev/null 2>&1 || echo "No image to remove."

# Clean up dangling images and volumes
echo "Cleaning up dangling images and volumes..."
docker image prune -f

docker volume prune -f

echo "Cleanup complete."


