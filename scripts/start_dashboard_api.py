#!/usr/bin/env python3
"""Start the MPtoO Dashboard API server."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import uvicorn

from src.infrastructure.dashboard.api import app

if __name__ == "__main__":
    print("Starting MPtoO Dashboard API on http://0.0.0.0:3002")
    uvicorn.run(app, host="0.0.0.0", port=3002, log_level="info")
