# Multi-stage Dockerfile for MPtoO

# Stage 1: Base image with ROCm support (for AMD GPUs)
FROM rocm/dev-ubuntu-22.04:latest AS base

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies and Python 3.11 (required by pyproject.toml)
RUN apt-get update && apt-get install -y \
    software-properties-common \
    git \
    curl \
    wget \
    build-essential \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    python3.11-distutils \
    && rm -rf /var/lib/apt/lists/*

# Create symbolic links for python
RUN ln -sf /usr/bin/python3.11 /usr/bin/python && \
    ln -sf /usr/bin/python3.11 /usr/bin/python3

# Install pip for Python 3.11
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# Upgrade pip
RUN python -m pip install --upgrade pip setuptools wheel

# Stage 2: Dependencies
FROM base AS dependencies

WORKDIR /tmp

# Copy only dependency files first (for better caching)
COPY pyproject.toml ./

# Install Python dependencies
# --ignore-installed blinker: ROCm base image has blinker 1.4 installed via distutils
# which pip cannot uninstall, so we force reinstall it
RUN pip install --no-cache-dir --ignore-installed blinker -e .

# Install PyTorch with ROCm support
# Note: Adjust rocm version based on your setup
RUN pip install --no-cache-dir \
    torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/rocm6.2

# Stage 3: Application
FROM dependencies AS application

WORKDIR /app

# Copy application code
COPY . .

# Install the application in development mode
RUN pip install --no-cache-dir --ignore-installed blinker -e ".[dev]"

# Create directories for data and models
RUN mkdir -p /data /models /logs

# Expose ports
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "src.interfaces.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Stage 4: Production (smaller image, no dev dependencies)
FROM base AS production

WORKDIR /app

# Copy only necessary files from dependencies stage
COPY --from=dependencies /usr/local/lib/python3.11/dist-packages /usr/local/lib/python3.11/dist-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY src ./src
COPY pyproject.toml ./

# Create non-root user
RUN useradd -m -u 1000 mptoo && \
    chown -R mptoo:mptoo /app

USER mptoo

# Create directories
RUN mkdir -p /app/data /app/models /app/logs

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "src.interfaces.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
