#!/bin/bash

# Script to update the repository and run the build script
set -euo pipefail

REPO_URL="https://github.com/amartyamandal/neuro-san-studio.git"  # Replace with your repository URL
CONTAINER_NAME="neuro-san-container"
DGO_FOLDER="dgo"

# Check if 'clean' argument is passed
if [[ "$*" == *"clean"* ]]; then
  echo "Running clean script..."
  bash "$DGO_FOLDER/clean_dgo.sh"
fi

# Stop the running container if it exists
echo "Stopping running container $CONTAINER_NAME if it exists..."
docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || echo "No running container to stop."

# Stash any local changes
echo "Stashing any local changes..."
git stash --include-untracked

# Pull the latest changes
echo "Cloning the repository..."
git pull "$REPO_URL"

# Make .sh files in dgo folder executable
echo "Making .sh files in $DGO_FOLDER executable..."
chmod +x $DGO_FOLDER/*.sh

# Run the build script
echo "Running $DGO_FOLDER/build_dgo_simple.sh..."
./$DGO_FOLDER/build_dgo_simple.sh
