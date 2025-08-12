# docker/dev/Dockerfile

# ─── 1) Base image & tools ─────────────────────────────────────────────────────
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=UTC

# Install Python 3.12 via deadsnakes PPA and curl
RUN apt-get update && apt-get install -y \
      software-properties-common \
      curl \
      gnupg \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y \
      python3.12 \
      python3.12-venv \
    && ln -sf /usr/bin/python3.12 /usr/bin/python3 \
    && ln -sf /usr/bin/python3.12 /usr/bin/python \
    && curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12 \
    && rm -rf /var/lib/apt/lists/*

# Create an isolated virtual environment and use it for all installs
ENV VIRTUAL_ENV=/opt/venv
RUN python3.12 -m venv "$VIRTUAL_ENV"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install only necessary dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r /app/requirements.txt

# Copy application files
COPY run.py /app/run.py
COPY apps/ /app/apps/

# Set working directory
WORKDIR /app

# Expose required ports (aligned with .env)
EXPOSE 4173 5001 8080 30011

# Set entrypoint to run the application
CMD ["python", "run.py"]