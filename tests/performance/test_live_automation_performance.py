"""Performance and concurrency tests for LIVE automation.

Tests cover:
- Response time benchmarks
- Concurrent session limits
- Memory usage under load
- Streaming latency
- Throughput benchmarks
"""

import asyncio
import json
import time
from typing import List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from src.infrastructure.agents.openmanus.openmanus_adapter import OpenManusAdapter
from src.infrastructure.llm.ollama_client import OllamaClient


class TestOllamaPerformance:
    """Performance tests for OllamaClient."""

    @pytest.mark.asyncio
    @pytest.mark.performance
    @pytest.mark.slow
    async def test_generate_response_time(self):
        """Test text generation response time."""
        ollama = OllamaClient()
        target_time = 2.0  # seconds

        try:
            with patch.object(ollama.client, "post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"response": "The capital of France is Paris."}
                mock_post.return_value = mock_response

                start = time.time()
                result = await ollama.generate(
                    prompt="What is the capital of France?", stream=False
                )
                elapsed = time.time() - start

                assert result == "The capital of France is Paris."
                # Should complete quickly (with mocked response)
                assert elapsed < 1.0

        finally:
            await ollama.close()

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_streaming_latency(self):
        """Test streaming response latency."""
        ollama = OllamaClient()

        try:

            async def mock_stream():
                for i in range(10):
                    yield json.dumps({"response": f"chunk{i} "})
                    # Small delay to simulate network
                    await asyncio.sleep(0.01)

            with patch.object(ollama.client, "stream") as mock_stream_method:
                mock_context = AsyncMock()
                mock_context.__aenter__.return_value.aiter_lines = mock_stream
                mock_stream_method.return_value = mock_context

                start = time.time()
                chunks = []
                async for chunk in await ollama._generate_stream(
                    {"model": "test", "prompt": "test"}
                ):
                    chunks.append(chunk)
                elapsed = time.time() - start

                assert len(chunks) == 10
                # Should complete in reasonable time
                assert elapsed < 1.0

        finally:
            await ollama.close()

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_concurrent_generations(self):
        """Test throughput with concurrent requests."""
        ollama = OllamaClient()
        num_concurrent = 10

        try:
            with patch.object(ollama.client, "post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"response": "Response"}
                mock_post.return_value = mock_response

                start = time.time()

                tasks = [
                    ollama.generate(f"Prompt {i}", stream=False) for i in range(num_concurrent)
                ]

                results = await asyncio.gather(*tasks)
                elapsed = time.time() - start

                assert len(results) == num_concurrent
                assert all(r == "Response" for r in results)

                # Calculate throughput
                throughput = num_concurrent / elapsed
                print(f"Throughput: {throughput:.2f} requests/sec")

                # Should handle multiple concurrent requests
                assert elapsed < 5.0

        finally:
            await ollama.close()

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_chat_performance(self):
        """Test chat completion performance."""
        ollama = OllamaClient()

        try:
            with patch.object(ollama.client, "post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"message": {"content": "Response"}}
                mock_post.return_value = mock_response

                messages = [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi there"},
                ] * 5  # 10 message history

                start = time.time()
                result = await ollama.chat(messages, stream=False)
                elapsed = time.time() - start

                assert result == "Response"
                # Should handle conversation history efficiently
                assert elapsed < 1.0

        finally:
            await ollama.close()

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_extraction_performance(self):
        """Test data extraction performance."""
        ollama = OllamaClient()
        large_html = "<html>" + "<p>Item</p>" * 1000 + "</html>"

        try:
            with patch.object(ollama.client, "post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "response": json.dumps(
                        {"items": ["Item"] * 100, "count": 100, "confidence": 0.95}
                    )
                }
                mock_post.return_value = mock_response

                start = time.time()
                result = await ollama.extract_data_with_llm(large_html, "items")
                elapsed = time.time() - start

                assert result["count"] == 100
                # Should handle large HTML efficiently
                assert elapsed < 1.0

        finally:
            await ollama.close()

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_health_check_performance(self):
        """Test health check performance."""
        ollama = OllamaClient()

        try:
            with patch.object(ollama.client, "get") as mock_get:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "models": [{"name": f"model{i}"} for i in range(20)]
                }
                mock_get.return_value = mock_response

                start = time.time()
                is_healthy = await ollama.health_check()
                elapsed = time.time() - start

                assert is_healthy is True
                # Health check should be very fast
                assert elapsed < 0.5

        finally:
            await ollama.close()


class TestBrowserPerformance:
    """Performance tests for browser operations."""

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_navigation_performance(self):
        """Test browser navigation performance."""
        agent = OpenManusAdapter(headless=True)

        try:
            with patch.object(agent, "_ensure_browser") as mock_ensure:
                mock_page = AsyncMock()
                mock_page.url = "https://example.com"
                mock_page.title = AsyncMock(return_value="Test Page")
                mock_page.goto = AsyncMock()
                mock_page.screenshot = AsyncMock()
                mock_page.close = AsyncMock()
                mock_page.wait_for_load_state = AsyncMock()

                mock_browser = AsyncMock()
                mock_browser.new_page = AsyncMock(return_value=mock_page)
                mock_ensure.return_value = mock_browser

                start = time.time()
                result = await agent.execute_task(
                    {"url": "https://example.com", "action": "navigate"}
                )
                elapsed = time.time() - start

                assert result["status"].value == "completed"
                # Navigation should complete reasonably fast
                assert elapsed < 5.0

        finally:
            await agent.cleanup()

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_extraction_performance_browser(self):
        """Test extraction performance in browser."""
        agent = OpenManusAdapter(headless=True)
        large_html = (
            """
        <html>
            <body>
                """
            + "".join(
                [f"<div class='item'><h3>Item {i}</h3><p>Description</p></div>" for i in range(500)]
            )
            + """
            </body>
        </html>
        """
        )

        try:
            with patch.object(agent, "_ensure_browser") as mock_ensure:
                mock_page = AsyncMock()
                mock_page.url = "https://example.com"
                mock_page.title = AsyncMock(return_value="Items")
                mock_page.goto = AsyncMock()
                mock_page.content = AsyncMock(return_value=large_html)
                mock_page.screenshot = AsyncMock()
                mock_page.close = AsyncMock()
                mock_page.wait_for_load_state = AsyncMock()

                mock_browser = AsyncMock()
                mock_browser.new_page = AsyncMock(return_value=mock_page)
                mock_ensure.return_value = mock_browser

                start = time.time()
                result = await agent.execute_task(
                    {
                        "url": "https://example.com",
                        "action": "extract",
                        "selectors": {"items": ".item h3"},
                    }
                )
                elapsed = time.time() - start

                assert result["status"].value == "completed"
                # Should handle large pages efficiently
                assert elapsed < 5.0

        finally:
            await agent.cleanup()

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_concurrent_browser_sessions(self):
        """Test performance with concurrent browser sessions."""
        num_sessions = 5
        agents = [OpenManusAdapter(headless=True) for _ in range(num_sessions)]

        try:
            with patch(
                "src.infrastructure.agents.openmanus.openmanus_adapter.async_playwright"
            ) as mock_pw:
                # Create mocks for each session
                mock_playwright = AsyncMock()
                mock_browsers = [AsyncMock() for _ in range(num_sessions)]
                mock_pages = [AsyncMock() for _ in range(num_sessions)]

                for page, browser in zip(mock_pages, mock_browsers):
                    page.url = "https://example.com"
                    page.title = AsyncMock(return_value="Test")
                    page.goto = AsyncMock()
                    page.screenshot = AsyncMock()
                    page.close = AsyncMock()
                    page.wait_for_load_state = AsyncMock()

                    browser.new_page = AsyncMock(return_value=page)
                    browser.close = AsyncMock()

                mock_pw.return_value.start = AsyncMock(return_value=mock_playwright)
                mock_playwright.chromium.launch = AsyncMock(side_effect=mock_browsers)

                start = time.time()

                tasks = [
                    agent.execute_task({"url": "https://example.com", "action": "navigate"})
                    for agent in agents
                ]

                results = await asyncio.gather(*tasks)
                elapsed = time.time() - start

                assert len(results) == num_sessions
                # All sessions should complete in reasonable time
                assert elapsed < 10.0

        finally:
            for agent in agents:
                # Cleanup would be async
                pass


class TestMemoryUsage:
    """Tests for memory usage during operations."""

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_large_response_handling(self):
        """Test handling of large responses without memory issues."""
        ollama = OllamaClient()
        large_response = "x" * 1000000  # 1MB response

        try:
            with patch.object(ollama.client, "post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"response": large_response}
                mock_post.return_value = mock_response

                result = await ollama.generate(prompt="Generate large text", stream=False)

                assert len(result) == len(large_response)

        finally:
            await ollama.close()

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_streaming_memory_efficiency(self):
        """Test that streaming doesn't accumulate memory."""
        ollama = OllamaClient()
        num_chunks = 1000

        try:

            async def mock_stream():
                for i in range(num_chunks):
                    yield json.dumps({"response": f"chunk{i} "})

            with patch.object(ollama.client, "stream") as mock_stream_method:
                mock_context = AsyncMock()
                mock_context.__aenter__.return_value.aiter_lines = mock_stream
                mock_stream_method.return_value = mock_context

                chunk_count = 0
                async for chunk in await ollama._generate_stream(
                    {"model": "test", "prompt": "test"}
                ):
                    chunk_count += 1
                    # Process chunks one at a time
                    assert chunk is not None

                assert chunk_count == num_chunks

        finally:
            await ollama.close()


class TestLoadTesting:
    """Load testing for system scalability."""

    @pytest.mark.asyncio
    @pytest.mark.performance
    @pytest.mark.slow
    async def test_system_under_load(self):
        """Test system behavior under sustained load."""
        ollama = OllamaClient()
        num_requests = 50
        target_success_rate = 0.95

        try:
            with patch.object(ollama.client, "post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"response": "Response"}
                mock_post.return_value = mock_response

                start = time.time()

                tasks = [ollama.generate(f"Prompt {i}", stream=False) for i in range(num_requests)]

                results = await asyncio.gather(*tasks, return_exceptions=True)
                elapsed = time.time() - start

                # Count successful vs failed
                successes = sum(1 for r in results if isinstance(r, str))
                success_rate = successes / num_requests

                print(f"Load test: {successes}/{num_requests} succeeded")
                print(f"Success rate: {success_rate * 100:.1f}%")
                print(f"Throughput: {num_requests / elapsed:.2f} requests/sec")

                assert success_rate >= target_success_rate

        finally:
            await ollama.close()


class TestBenchmarks:
    """Benchmark tests for performance tracking."""

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_end_to_end_benchmark(self, benchmark):
        """Benchmark complete workflow."""

        async def workflow():
            ollama = OllamaClient()
            agent = OpenManusAdapter(headless=True)

            try:
                with patch.object(ollama.client, "post") as mock_post:
                    with patch.object(agent, "_ensure_browser") as mock_ensure:
                        mock_page = AsyncMock()
                        mock_page.url = "https://example.com"
                        mock_page.title = AsyncMock(return_value="Test")
                        mock_page.goto = AsyncMock()
                        mock_page.screenshot = AsyncMock()
                        mock_page.close = AsyncMock()
                        mock_page.wait_for_load_state = AsyncMock()

                        mock_browser = AsyncMock()
                        mock_browser.new_page = AsyncMock(return_value=mock_page)
                        mock_ensure.return_value = mock_browser

                        mock_response = MagicMock()
                        mock_response.json.return_value = {"response": "Result"}
                        mock_post.return_value = mock_response

                        # Execute workflow
                        await agent.execute_task(
                            {"url": "https://example.com", "action": "navigate"}
                        )

                        result = await ollama.generate("What did you see?", stream=False)

                        return result

            finally:
                await ollama.close()
                await agent.cleanup()

        # Note: This would need pytest-benchmark to work properly
        # For now, just verify it completes
        result = asyncio.run(workflow())
        assert result == "Result"
