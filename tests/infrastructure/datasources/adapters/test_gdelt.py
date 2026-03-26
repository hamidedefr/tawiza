"""Tests for GDELT news adapter."""

import pytest

from src.infrastructure.datasources.adapters.gdelt import GdeltAdapter

# Skip - requires GDELT API access (network, flaky)
pytestmark = pytest.mark.skipif(True, reason="Requires GDELT API (network, flaky)")


@pytest.mark.asyncio
async def test_gdelt_health_check():
    """Test GDELT API health check."""
    adapter = GdeltAdapter()
    healthy = await adapter.health_check()
    assert healthy is True


@pytest.mark.asyncio
async def test_gdelt_search_by_keyword():
    """Test searching news by keyword."""
    adapter = GdeltAdapter()
    results = await adapter.search(
        {
            "keywords": "startup France",
            "limit": 5,
        }
    )
    assert len(results) > 0
    assert "title" in results[0]
    assert "url" in results[0]
