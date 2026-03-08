#!/bin/bash
# Setup script for VM-400 Sandbox Service
# Run this on VM-400 (192.168.1.100)

set -e

echo "=== MPtoO Sandbox Service Setup ==="

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    usermod -aG docker $USER
fi

# Pull required images
echo "Pulling Docker images..."
docker pull python:3.12-slim
docker pull ubuntu:22.04

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install fastapi uvicorn docker pydantic httpx

# Create systemd service
echo "Creating systemd service..."
cat > /etc/systemd/system/mptoo-sandbox.service << 'EOF'
[Unit]
Description=MPtoO Sandbox Service
After=docker.service
Requires=docker.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/mptoo-sandbox
Environment=SANDBOX_API_KEY=mptoo-sandbox-key-2024
ExecStart=/usr/bin/python3 -m uvicorn sandbox_service:app --host 0.0.0.0 --port 8100
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Copy service file
mkdir -p /opt/mptoo-sandbox
cp sandbox_service.py /opt/mptoo-sandbox/

# Enable and start service
systemctl daemon-reload
systemctl enable mptoo-sandbox
systemctl start mptoo-sandbox

echo "=== Setup Complete ==="
echo "Service running on http://0.0.0.0:8100"
echo "Test with: curl http://localhost:8100/health"
