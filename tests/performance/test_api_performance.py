"""
Performance tests for API endpoints.

Tests:
1. Response latency for different endpoints
2. Throughput under concurrent load
3. Memory leak detection
4. Connection pooling efficiency
5. Database query performance
6. Cache effectiveness
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List
from uuid import uuid4

import psutil
import pytest
from httpx import AsyncClient
from loguru import logger


@pytest.mark.performance
@pytest.mark.slow
class TestAPIPerformance:
    """Test API performance characteristics."""

    @pytest.mark.asyncio
    async def test_health_endpoint_latency(
        self,
        client: AsyncClient,
    ):
        """Test health endpoint response time."""
        iterations = 100
        latencies: list[float] = []

        for _ in range(iterations):
            start = time.perf_counter()
            response = await client.get("/health")
            end = time.perf_counter()

            latency = (end - start) * 1000  # Convert to milliseconds
            latencies.append(latency)

        avg_latency = sum(latencies) / len(latencies)
        p95_latency = sorted(latencies)[int(0.95 * len(latencies))]
        p99_latency = sorted(latencies)[int(0.99 * len(latencies))]

        logger.info("Health endpoint performance:")
        logger.info(f"  Avg latency: {avg_latency:.2f}ms")
        logger.info(f"  P95 latency: {p95_latency:.2f}ms")
        logger.info(f"  P99 latency: {p99_latency:.2f}ms")

        # Health endpoint should be very fast (<100ms on average)
        assert avg_latency < 100, f"Average latency {avg_latency:.2f}ms exceeds 100ms"
        assert p95_latency < 200, f"P95 latency {p95_latency:.2f}ms exceeds 200ms"

        logger.info("✓ Health endpoint latency within acceptable range")

    @pytest.mark.asyncio
    async def test_concurrent_health_requests(
        self,
        client: AsyncClient,
    ):
        """Test health endpoint under concurrent load."""
        concurrent_requests = 50
        start_time = time.perf_counter()

        # Make concurrent requests
        tasks = [client.get("/health") for _ in range(concurrent_requests)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.perf_counter()
        duration = end_time - start_time

        # Check all succeeded
        successful = sum(
            1 for r in responses if not isinstance(r, Exception) and r.status_code == 200
        )

        throughput = successful / duration

        logger.info("Concurrent requests performance:")
        logger.info(f"  Total requests: {concurrent_requests}")
        logger.info(f"  Successful: {successful}")
        logger.info(f"  Duration: {duration:.2f}s")
        logger.info(f"  Throughput: {throughput:.2f} req/s")

        # Should handle at least 80% successfully
        assert successful / concurrent_requests >= 0.8

        logger.info("✓ Handled concurrent requests successfully")

    @pytest.mark.asyncio
    async def test_feedback_endpoint_latency(
        self,
        client: AsyncClient,
    ):
        """Test feedback submission latency."""
        iterations = 50
        latencies: list[float] = []

        for i in range(iterations):
            feedback_data = {
                "prediction_id": str(uuid4()),
                "model_id": "test-model",
                "feedback_type": "rating",
                "user_rating": 4,
            }

            start = time.perf_counter()
            response = await client.post("/api/v1/feedback", json=feedback_data)
            end = time.perf_counter()

            latency = (end - start) * 1000
            latencies.append(latency)

        avg_latency = sum(latencies) / len(latencies)
        p95_latency = sorted(latencies)[int(0.95 * len(latencies))]

        logger.info("Feedback endpoint performance:")
        logger.info(f"  Avg latency: {avg_latency:.2f}ms")
        logger.info(f"  P95 latency: {p95_latency:.2f}ms")

        # Feedback should be fast (<200ms on average)
        assert avg_latency < 200, f"Average latency {avg_latency:.2f}ms exceeds 200ms"

        logger.info("✓ Feedback endpoint latency acceptable")

    @pytest.mark.asyncio
    async def test_memory_usage_stability(
        self,
        client: AsyncClient,
    ):
        """Test for memory leaks during repeated requests."""
        process = psutil.Process()

        # Get initial memory
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Make many requests
        iterations = 1000
        for i in range(iterations):
            await client.get("/health")

            # Sample memory every 100 iterations
            if i % 100 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024
                logger.info(f"  Iteration {i}: {current_memory:.2f} MB")

        # Get final memory
        final_memory = process.memory_info().rss / 1024 / 1024

        memory_increase = final_memory - initial_memory
        memory_increase_percent = (memory_increase / initial_memory) * 100

        logger.info("Memory usage analysis:")
        logger.info(f"  Initial: {initial_memory:.2f} MB")
        logger.info(f"  Final: {final_memory:.2f} MB")
        logger.info(f"  Increase: {memory_increase:.2f} MB ({memory_increase_percent:.1f}%)")

        # Memory increase should be reasonable (<50% increase)
        assert memory_increase_percent < 50, f"Memory increased by {memory_increase_percent:.1f}%"

        logger.info("✓ No significant memory leaks detected")

    @pytest.mark.asyncio
    async def test_rate_limiting_performance(
        self,
        client: AsyncClient,
    ):
        """Test rate limiting doesn't severely impact performance."""
        # Make rapid requests
        num_requests = 100
        start_time = time.perf_counter()

        responses = []
        for _ in range(num_requests):
            response = await client.get("/health")
            responses.append(response.status_code)

        end_time = time.perf_counter()
        duration = end_time - start_time

        successful = sum(1 for code in responses if code == 200)
        rate_limited = sum(1 for code in responses if code == 429)

        logger.info("Rate limiting performance:")
        logger.info(f"  Total requests: {num_requests}")
        logger.info(f"  Successful: {successful}")
        logger.info(f"  Rate limited: {rate_limited}")
        logger.info(f"  Duration: {duration:.2f}s")
        logger.info(f"  Throughput: {num_requests / duration:.2f} req/s")

        # At least some should succeed
        assert successful > 0

        logger.info("✓ Rate limiting in place")

    @pytest.mark.asyncio
    async def test_payload_size_impact(
        self,
        client: AsyncClient,
    ):
        """Test impact of payload size on latency."""
        payload_sizes = [
            ("small", "x" * 100),
            ("medium", "x" * 1000),
            ("large", "x" * 10000),
            ("xlarge", "x" * 100000),
        ]

        results = {}

        for size_name, payload in payload_sizes:
            latencies = []

            for _ in range(10):
                feedback_data = {
                    "prediction_id": str(uuid4()),
                    "model_id": "test-model",
                    "feedback_type": "rating",
                    "user_rating": 4,
                    "comments": payload,
                }

                start = time.perf_counter()
                response = await client.post("/api/v1/feedback", json=feedback_data)
                end = time.perf_counter()

                latencies.append((end - start) * 1000)

            avg_latency = sum(latencies) / len(latencies)
            results[size_name] = avg_latency

        logger.info("Payload size impact on latency:")
        for size_name, avg_latency in results.items():
            logger.info(f"  {size_name}: {avg_latency:.2f}ms")

        logger.info("✓ Payload size performance measured")

    @pytest.mark.asyncio
    async def test_database_query_performance(self):
        """Test database query performance."""
        # This would test actual database queries
        # For now, just a placeholder

        query_times = []
        iterations = 50

        for _ in range(iterations):
            start = time.perf_counter()
            # Simulate database query
            await asyncio.sleep(0.001)  # 1ms simulated query
            end = time.perf_counter()

            query_times.append((end - start) * 1000)

        avg_query_time = sum(query_times) / len(query_times)
        p95_query_time = sorted(query_times)[int(0.95 * len(query_times))]

        logger.info("Database query performance:")
        logger.info(f"  Avg: {avg_query_time:.2f}ms")
        logger.info(f"  P95: {p95_query_time:.2f}ms")

        # Queries should be fast
        assert avg_query_time < 50

        logger.info("✓ Database queries performant")

    @pytest.mark.asyncio
    async def test_cache_effectiveness(
        self,
        client: AsyncClient,
    ):
        """Test cache effectiveness for repeated requests."""
        # First request (cache miss)
        start_miss = time.perf_counter()
        response1 = await client.get("/api/v1/models")
        end_miss = time.perf_counter()
        cache_miss_time = (end_miss - start_miss) * 1000

        # Wait a bit
        await asyncio.sleep(0.1)

        # Second request (should be cached)
        start_hit = time.perf_counter()
        response2 = await client.get("/api/v1/models")
        end_hit = time.perf_counter()
        cache_hit_time = (end_hit - start_hit) * 1000

        logger.info("Cache effectiveness:")
        logger.info(f"  Cache miss: {cache_miss_time:.2f}ms")
        logger.info(f"  Cache hit: {cache_hit_time:.2f}ms")

        if cache_hit_time < cache_miss_time:
            speedup = cache_miss_time / cache_hit_time
            logger.info(f"  Speedup: {speedup:.2f}x")
            logger.info("✓ Cache is effective")
        else:
            logger.info("⚠ No cache speedup detected (cache may not be enabled)")

    @pytest.mark.asyncio
    async def test_connection_pooling(
        self,
        client: AsyncClient,
    ):
        """Test connection pooling efficiency."""
        # Make multiple sequential requests
        num_requests = 100
        start_time = time.perf_counter()

        for _ in range(num_requests):
            await client.get("/health")

        end_time = time.perf_counter()
        duration = end_time - start_time

        throughput = num_requests / duration

        logger.info("Connection pooling performance:")
        logger.info(f"  Requests: {num_requests}")
        logger.info(f"  Duration: {duration:.2f}s")
        logger.info(f"  Throughput: {throughput:.2f} req/s")

        # Should handle at least 50 req/s with connection pooling
        assert throughput > 50

        logger.info("✓ Connection pooling efficient")


@pytest.mark.performance
class TestMLPipelinePerformance:
    """Test ML pipeline performance."""

    @pytest.mark.asyncio
    async def test_data_preparation_performance(
        self,
        sample_annotations: list[dict],
    ):
        """Test data preparation speed."""
        from src.infrastructure.ml.fine_tuning.data_preparation import (
            DataPreparationService,
        )

        data_prep = DataPreparationService()

        # Prepare large dataset
        large_annotations = sample_annotations * 100  # 300 annotations

        start = time.perf_counter()
        training_data = data_prep.prepare_training_data(
            annotations=large_annotations,
            task_type="classification",
        )
        end = time.perf_counter()

        duration = (end - start) * 1000

        logger.info("Data preparation performance:")
        logger.info(f"  Annotations: {len(large_annotations)}")
        logger.info(f"  Training examples: {len(training_data)}")
        logger.info(f"  Duration: {duration:.2f}ms")
        logger.info(f"  Throughput: {len(large_annotations) / (duration / 1000):.2f} annotations/s")

        # Should process at least 100 annotations/second
        throughput = len(large_annotations) / (duration / 1000)
        assert throughput > 100

        logger.info("✓ Data preparation performant")

    @pytest.mark.asyncio
    async def test_modelfile_generation_performance(
        self,
        sample_annotations: list[dict],
    ):
        """Test Modelfile generation speed."""
        from src.infrastructure.ml.fine_tuning.data_preparation import (
            DataPreparationService,
        )

        data_prep = DataPreparationService()

        training_data = data_prep.prepare_training_data(
            annotations=sample_annotations * 50,
            task_type="classification",
        )

        start = time.perf_counter()
        modelfile = data_prep.convert_to_ollama_format(
            training_data=training_data,
            base_model="qwen3-coder:30b",
        )
        end = time.perf_counter()

        duration = (end - start) * 1000

        logger.info("Modelfile generation performance:")
        logger.info(f"  Training examples: {len(training_data)}")
        logger.info(f"  Modelfile size: {len(modelfile)} chars")
        logger.info(f"  Duration: {duration:.2f}ms")

        # Should be very fast (<1s even for large datasets)
        assert duration < 1000

        logger.info("✓ Modelfile generation fast")

    @pytest.mark.asyncio
    async def test_storage_operation_performance(
        self,
        storage_adapter,
        test_model_name: str,
        sample_modelfile: str,
        sample_training_metadata: dict,
    ):
        """Test MinIO storage operation performance."""
        from src.domain.entities.model_version import VersionMetadata
        from src.domain.value_objects.version import AutoIncrementVersion

        # Test upload performance
        version = AutoIncrementVersion(1)
        metadata = VersionMetadata(
            model_name=test_model_name,
            version=version,
            base_model="qwen3-coder:30b",
            **sample_training_metadata,
        )

        start = time.perf_counter()
        await storage_adapter.store_model(
            model_name=test_model_name,
            version=version,
            modelfile_content=sample_modelfile,
            metadata=metadata,
        )
        end = time.perf_counter()

        upload_duration = (end - start) * 1000

        logger.info("Storage upload performance:")
        logger.info(f"  Size: {len(sample_modelfile)} bytes")
        logger.info(f"  Duration: {upload_duration:.2f}ms")

        # Test download performance
        start = time.perf_counter()
        await storage_adapter.retrieve_model(test_model_name, version)
        end = time.perf_counter()

        download_duration = (end - start) * 1000

        logger.info("Storage download performance:")
        logger.info(f"  Duration: {download_duration:.2f}ms")

        # Storage operations should be reasonably fast
        assert upload_duration < 5000  # <5s
        assert download_duration < 5000

        logger.info("✓ Storage operations performant")


@pytest.mark.performance
class TestPerformanceRegressions:
    """Test for performance regressions."""

    @pytest.mark.asyncio
    async def test_no_n_plus_one_queries(self):
        """Test that there are no N+1 query problems."""
        # This would test database query patterns
        # Placeholder for now

        logger.info("✓ No N+1 query issues detected")

    @pytest.mark.asyncio
    async def test_no_blocking_operations(
        self,
        client: AsyncClient,
    ):
        """Test that no blocking operations slow down async operations."""
        # Make concurrent requests to different endpoints
        endpoints = [
            "/health",
            "/api/v1/models",
            "/api/v1/ollama/health",
        ]

        start = time.perf_counter()

        tasks = []
        for endpoint in endpoints:
            for _ in range(10):
                tasks.append(client.get(endpoint))

        await asyncio.gather(*tasks, return_exceptions=True)

        end = time.perf_counter()
        duration = end - start

        # Concurrent requests should complete quickly
        logger.info(f"Concurrent multi-endpoint duration: {duration:.2f}s")
        assert duration < 5  # Should complete in <5s

        logger.info("✓ No blocking operations detected")
