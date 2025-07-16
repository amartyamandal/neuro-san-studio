#!/usr/bin/env bash
set -euo pipefail

# ----------------------------------------------------------------------
# setup_codex.sh
# Script used by Codex to build the environment and execute the tests.
# It mirrors the behaviour of the Docker development container but runs
# directly on the host.
# ----------------------------------------------------------------------

# Prefer Python 3.12 if available, otherwise fall back to the default python3.
PYTHON="python3.12"
if ! command -v "$PYTHON" >/dev/null 2>&1; then
    PYTHON="python3"
fi

# Create a virtual environment in ./venv
"$PYTHON" -m venv venv
source venv/bin/activate

# Install runtime and build dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r requirements-build.txt

# Run the test suite with coverage as configured in pyproject.toml
python -m pytest tests -v --cov=coded_tools --cov=apps --cov-report=term-missing