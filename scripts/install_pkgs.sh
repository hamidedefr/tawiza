#!/bin/bash
set -e

echo "=== MPtoO-V2 Claude Code Cloud Setup ==="

# Detect if running in Claude Code cloud environment
if [ -n "$CLAUDE_CODE_REMOTE" ]; then
    echo "Running in Claude Code cloud environment"

    # Create Python virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "Creating Python virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment
    echo "Activating virtual environment..."
    source venv/bin/activate

    # Upgrade pip
    echo "Upgrading pip..."
    pip install --upgrade pip --quiet

    # Install dependencies
    echo "Installing Python dependencies..."
    pip install -r requirements.txt --quiet

    # Install the package in editable mode
    echo "Installing mptoo package in editable mode..."
    pip install -e . --quiet

    # Check if Docker is available
    if command -v docker &> /dev/null; then
        echo "Docker detected, starting services..."

        # Start core services (postgres, redis, minio)
        docker-compose up -d postgres redis minio mlflow

        # Wait for services to be ready
        echo "Waiting for services to be ready..."
        sleep 10

        # Run database migrations
        echo "Running database migrations..."
        alembic upgrade head || true

        echo "Services started successfully!"
        docker-compose ps
    else
        echo "Docker not available in this environment"
        echo "Some features may not work without backend services"
    fi

    echo ""
    echo "=== Setup Complete ==="
    echo "You can now use the 'mptoo' CLI:"
    echo "  mptoo --help"
    echo "  mptoo system status"
    echo "  mptoo models list"
    echo ""
else
    echo "Running in local environment"
    echo "Please ensure services are started with: docker-compose up -d"
fi

exit 0
