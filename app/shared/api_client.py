"""API client for FastAPI backend."""

from dataclasses import dataclass
from typing import Any, Optional

import httpx


@dataclass
class APIConfig:
    """API configuration."""

    base_url: str = "http://localhost:8000"
    timeout: float = 30.0


class APIClient:
    """Client for MPtoO FastAPI backend."""

    def __init__(self, config: APIConfig | None = None) -> None:
        self.config = config or APIConfig()

    async def health_check(self) -> dict[str, Any]:
        """Check API health."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.config.base_url}/health", timeout=self.config.timeout
            )
            return response.json()

    async def start_evaluation(
        self, question: str, territory: str | None = None, sources: list[str] | None = None
    ) -> dict[str, Any]:
        """Start a new evaluation."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.config.base_url}/api/v1/evaluations",
                json={"question": question, "territory": territory, "sources": sources or []},
                timeout=self.config.timeout,
            )
            return response.json()

    async def get_evaluation(self, evaluation_id: str) -> dict[str, Any]:
        """Get evaluation status and results."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.config.base_url}/api/v1/evaluations/{evaluation_id}",
                timeout=self.config.timeout,
            )
            return response.json()

    async def list_models(self) -> list[dict[str, Any]]:
        """List available Ollama models."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.config.base_url}/api/v1/models", timeout=self.config.timeout
            )
            return response.json()
