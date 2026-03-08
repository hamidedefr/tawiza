#!/usr/bin/env python3
"""Entry point for MPtoO CLI v2."""

import sys
from pathlib import Path


def main():
    """Main entry point."""
    # Add project root to path
    project_root = Path(__file__).parent.parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # Import and run the v2 app with correct prog_name for shell completion
    from src.cli.v2.app import app

    # Pass prog_name="mptoo" so shell completion uses _MPTOO_COMPLETE
    app(prog_name="mptoo")


if __name__ == "__main__":
    main()
