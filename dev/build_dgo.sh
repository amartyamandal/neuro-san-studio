#!/usr/bin/env bash

# DigitalOcean Droplet bootstrap for neuro-san-studio
# - Installs Docker on Ubuntu
# - Clones repo (branch: cognizant-ai-lab-main)
# - Builds dev image and runs container exposing ports 4173, 5001, 8080, 30011
# - Uses dev/entrypoint_simple.sh to start services inside the container

set -euo pipefail

REPO_URL="https://github.com/amartyamandal/neuro-san-studio.git"
REPO_BRANCH="cognizant-ai-lab-main"
INSTALL_DIR="${INSTALL_DIR:-/opt/neuro-san-studio}"
IMAGE_NAME="neuro-san-dev"
CONTAINER_NAME="neuro-san-container"
VOLUME_NAME="neuro-san-studio-history"
CONTAINER_APP_DIR="${CONTAINER_APP_DIR:-/home/user/app}"
CLEANED="false"

# Use sudo only if not running as root
if [ "$(id -u)" -eq 0 ]; then
  SUDO=""
else
  SUDO="sudo"
fi

echo "[Setup] Starting bootstrap for neuro-san-studio"

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "[Error] Required command '$1' not found."; exit 1; }
}

detect_ubuntu() {
  if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [ "${ID:-}" != "ubuntu" ]; then
      echo "[Warn] Non-Ubuntu detected ($ID). This script is tested on Ubuntu. Continuing..."
    fi
  fi
}

install_docker() {
  if command -v docker >/dev/null 2>&1; then
    echo "[Docker] Docker already installed"
    return
  fi
  echo "[Docker] Installing Docker Engine..."
  $SUDO apt-get update -y
  $SUDO apt-get install -y ca-certificates curl gnupg lsb-release
  $SUDO install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | $SUDO gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    $SUDO tee /etc/apt/sources.list.d/docker.list >/dev/null
  $SUDO apt-get update -y
  $SUDO apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin git
  $SUDO systemctl enable docker
  $SUDO systemctl start docker
  echo "[Docker] Installed Docker Engine"
}

prepare_install_dir() {
  echo "[Repo] Preparing install dir: $INSTALL_DIR"
  $SUDO mkdir -p "$INSTALL_DIR"
  # If running as non-root, give ownership so docker bind mounts work smoothly
  if [ -n "${SUDO_USER:-}" ]; then
    $SUDO chown -R "$SUDO_USER":"$SUDO_USER" "$INSTALL_DIR"
  else
    $SUDO chown -R "$USER":"$USER" "$INSTALL_DIR"
  fi
}

clone_repo() {
  if [ -d "$INSTALL_DIR/.git" ]; then
    echo "[Repo] Existing git repo found. Pulling latest on branch $REPO_BRANCH..."
    git -C "$INSTALL_DIR" fetch origin "$REPO_BRANCH"
    git -C "$INSTALL_DIR" checkout "$REPO_BRANCH"
    git -C "$INSTALL_DIR" pull --ff-only origin "$REPO_BRANCH"
  else
    echo "[Repo] Cloning $REPO_URL (branch: $REPO_BRANCH) into $INSTALL_DIR"
    git clone --branch "$REPO_BRANCH" --single-branch "$REPO_URL" "$INSTALL_DIR"
  fi
}

ensure_env_file() {
  cd "$INSTALL_DIR"
  if [ ! -f .env ]; then
    echo "[Env] Creating .env with placeholders (edit as needed)"
    cat > .env <<'EOF'
# --- Required for remote TTS (optional, but recommended) ---
ENABLE_OPENAI_TTS=true
OPENAI_API_KEY=
OPENAI_TTS_MODEL=tts-1
OPENAI_TTS_VOICE=coral
OPENAI_TTS_FORMAT=mp3
OPENAI_TTS_TEMPERATURE=0.6

# You can add other application environment variables here
EOF
  else
    echo "[Env] Using existing .env"
  fi
}

build_image() {
  cd "$INSTALL_DIR"
  echo "[Build] Building image $IMAGE_NAME using dev/Dockerfile"
  $SUDO docker build -t "$IMAGE_NAME" -f dev/Dockerfile .
}

ensure_volume() {
  if $SUDO docker volume inspect "$VOLUME_NAME" >/dev/null 2>&1; then
    echo "[Docker] Volume $VOLUME_NAME exists"
  else
    echo "[Docker] Creating volume $VOLUME_NAME"
    $SUDO docker volume create "$VOLUME_NAME" >/dev/null
  fi
}

stop_existing_container() {
  if $SUDO docker ps -a --format '{{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
    echo "[Docker] Stopping/removing existing container $CONTAINER_NAME"
    $SUDO docker rm -f "$CONTAINER_NAME" >/dev/null || true
  fi
}

# Optionally cleanup existing installation and Docker artifacts
maybe_cleanup() {
  local choice
  choice="${CLEANUP:-}"
  if [ -z "$choice" ]; then
    echo -n "Cleanup existing neuro-san-studio and redo installation? [y/N]: "
    read -r choice || choice="n"
  fi
  case "${choice,,}" in
    y|yes)
      echo "[Cleanup] Starting cleanup..."
      if [ -f "$INSTALL_DIR/dev/clean_dgo.sh" ]; then
        echo "[Cleanup] Using clean script: $INSTALL_DIR/dev/clean_dgo.sh"
        $SUDO chmod +x "$INSTALL_DIR/dev/clean_dgo.sh" || true
        "$INSTALL_DIR/dev/clean_dgo.sh" || true
      else
        echo "[Cleanup] Clean script not found. Performing inline cleanup."
        $SUDO docker rm -f "$CONTAINER_NAME" || true
        $SUDO docker rmi -f "$IMAGE_NAME" || true
        $SUDO docker image prune -f || true
        $SUDO docker volume rm "$VOLUME_NAME" || true
        if command -v ufw >/dev/null 2>&1; then
          $SUDO ufw delete allow 4173/tcp || true
          $SUDO ufw delete allow 5001/tcp || true
          $SUDO ufw delete allow 8080/tcp || true
          $SUDO ufw delete allow 30011/tcp || true
        fi
        $SUDO rm -rf "$INSTALL_DIR" || true
      fi
      CLEANED="true"
      ;;
    *)
      echo "[Cleanup] Skipped."
      ;;
  esac
}

run_container() {
  cd "$INSTALL_DIR"
  echo "[Run] Starting container $CONTAINER_NAME"
  # Ensure entrypoint is executable on host to avoid permission issues inside container
  $SUDO chmod +x "$INSTALL_DIR/dev/entrypoint_simple.sh" || true
  echo "[Run] Mounting host: $INSTALL_DIR -> container: $CONTAINER_APP_DIR"
  # Ports:
  # 4173   -> nsflow client (UI)
  # 30011  -> Neuro-SAN gRPC server
  # 8080   -> Neuro-SAN HTTP server
  # 5001   -> CRUSE / Flask SocketIO UI
  $SUDO docker run -d --env-file .env --name "$CONTAINER_NAME" \
    --restart unless-stopped \
    -p 4173:4173 \
    -p 30011:30011 \
    -p 8080:8080 \
    -p 5001:5001 \
    -v "$VOLUME_NAME:/home/user/" \
    -v "$INSTALL_DIR:$CONTAINER_APP_DIR" \
    --entrypoint bash \
  "$IMAGE_NAME" -lc "bash $CONTAINER_APP_DIR/dev/entrypoint_simple.sh; sleep infinity"

  echo "[Run] Container launched. Use: $SUDO docker logs -f $CONTAINER_NAME"
}

open_firewall_ports() {
  # Try to allow ports via ufw if present/enabled
  if command -v ufw >/dev/null 2>&1; then
    echo "[Firewall] Opening ports 4173 and 5001 via ufw (if ufw is active)"
  $SUDO ufw allow 4173/tcp || true
  $SUDO ufw allow 5001/tcp || true
  $SUDO ufw allow 8080/tcp || true
  $SUDO ufw allow 30011/tcp || true
  else
    echo "[Firewall] ufw not installed; skipping. Ensure cloud firewall allows: 4173, 5001, 8080, 30011"
  fi
}

post_notes() {
  echo ""
  echo "[Next] Verify services are up:"
  echo "  - Public IP: curl -s ifconfig.me (or check your DO droplet dashboard)"
  echo "  - CRUSE UI:   http://<PUBLIC_IP>:5001/"
  echo "  - NS UI:      http://<PUBLIC_IP>:4173/ (if applicable in your workflow)"
  echo "  - Logs:       $SUDO docker logs -f $CONTAINER_NAME"
  echo ""
  echo "[Control] Common docker commands:"
  echo "  $SUDO docker ps"
  echo "  $SUDO docker logs -f $CONTAINER_NAME"
  echo "  $SUDO docker restart $CONTAINER_NAME"
  echo "  $SUDO docker stop $CONTAINER_NAME && $SUDO docker rm $CONTAINER_NAME"
}

main() {
  detect_ubuntu
  install_docker
  # First ensure we have the repo locally (so we can run its clean script if present)
  prepare_install_dir
  clone_repo
  # Then optionally clean up; if cleaned, re-clone to restore the repo
  maybe_cleanup
  if [ "$CLEANED" = "true" ]; then
    prepare_install_dir
    clone_repo
  fi
  ensure_env_file
  build_image
  ensure_volume
  stop_existing_container
  open_firewall_ports
  run_container
  post_notes
}

main "$@"
