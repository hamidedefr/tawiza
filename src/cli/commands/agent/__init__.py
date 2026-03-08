"""Autonomous agent CLI commands.

Provides commands for LLM-guided browser automation:
- mptoo agent run: Execute autonomous task
- mptoo agent plan: Generate and show execution plan
- mptoo agent status: Show execution status
- mptoo agent cancel: Cancel running task
- mptoo agent resume: Resume paused task
"""

from src.cli.commands.agent.commands import app

__all__ = ["app"]
