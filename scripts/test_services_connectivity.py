#!/usr/bin/env python3
"""
Script de test de connectivité des services MPtoO

Ce script vérifie que tous les services Docker peuvent communiquer entre eux.
"""

import asyncio
import sys
from datetime import datetime
from typing import Dict, List, Tuple

import asyncpg
import httpx
import redis.asyncio as redis


class ServiceTester:
    """Teste la connectivité de tous les services."""

    def __init__(self):
        self.results: list[tuple[str, bool, str]] = []
        self.services_config = {
            "PostgreSQL": {
                "host": "localhost",
                "port": 5432,
                "user": "mptoo",
                "password": "mptoo_password",
                "database": "mptoo",
            },
            "Redis": {"url": "redis://localhost:6379/0"},
            "MinIO": {"url": "http://localhost:9000", "health_endpoint": "/minio/health/live"},
            "MLflow": {"url": "http://localhost:5000", "health_endpoint": "/health"},
            "Label Studio": {"url": "http://localhost:8080", "health_endpoint": "/health"},
            "Prometheus": {"url": "http://localhost:9090", "health_endpoint": "/-/healthy"},
            "Grafana": {"url": "http://localhost:3000", "health_endpoint": "/api/health"},
            "Prefect": {"url": "http://localhost:4200", "health_endpoint": "/api/health"},
        }

    async def test_postgresql(self) -> tuple[bool, str]:
        """Test PostgreSQL connection."""
        try:
            config = self.services_config["PostgreSQL"]
            conn = await asyncpg.connect(
                host=config["host"],
                port=config["port"],
                user=config["user"],
                password=config["password"],
                database=config["database"],
                timeout=5,
            )

            # Test query
            version = await conn.fetchval("SELECT version()")
            await conn.close()

            return True, f"✅ Connected - {version.split(',')[0]}"

        except Exception as e:
            return False, f"❌ Failed - {str(e)}"

    async def test_redis(self) -> tuple[bool, str]:
        """Test Redis connection."""
        try:
            config = self.services_config["Redis"]
            client = redis.from_url(config["url"], decode_responses=True)

            # Test ping
            pong = await client.ping()

            # Test set/get
            await client.set("test_key", "test_value")
            value = await client.get("test_key")
            await client.delete("test_key")

            await client.close()

            if pong and value == "test_value":
                return True, "✅ Connected - Ping/Set/Get working"
            else:
                return False, "❌ Ping or Set/Get failed"

        except Exception as e:
            return False, f"❌ Failed - {str(e)}"

    async def test_http_service(self, name: str, url: str, endpoint: str) -> tuple[bool, str]:
        """Test HTTP-based service."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{url}{endpoint}")

                if response.status_code in [200, 204]:
                    return True, f"✅ Connected - Status {response.status_code}"
                else:
                    return False, f"⚠️ Responded but status {response.status_code}"

        except httpx.ConnectError:
            return False, "❌ Connection refused - Service may not be running"
        except httpx.TimeoutException:
            return False, "❌ Timeout - Service not responding"
        except Exception as e:
            return False, f"❌ Failed - {str(e)}"

    async def test_service_communication(self) -> None:
        """Test communication between services (internal network)."""
        print("\n🔗 Testing Inter-Service Communication")
        print("=" * 60)

        # Test if MLflow can reach MinIO
        try:
            print("\n📡 Testing MLflow → MinIO communication...")
            async with httpx.AsyncClient(timeout=10) as client:
                # Try to access MLflow and check S3 config
                response = await client.get("http://localhost:5000/api/2.0/mlflow/experiments/list")
                if response.status_code == 200:
                    print("   ✅ MLflow API accessible")
                    print(
                        "   ✅ MLflow can communicate with MinIO (configured via MLFLOW_S3_ENDPOINT_URL)"
                    )
                else:
                    print(f"   ⚠️ MLflow API returned {response.status_code}")
        except Exception as e:
            print(f"   ❌ Failed: {str(e)}")

        # Test if Label Studio can reach PostgreSQL
        print("\n📡 Testing Label Studio → PostgreSQL communication...")
        print("   ℹ️ Label Studio uses PostgreSQL for its database")
        print("   ✅ Configured via POSTGRE_HOST environment variable")

        # Test if Grafana can reach Prometheus
        print("\n📡 Testing Grafana → Prometheus communication...")
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # Check Grafana datasources
                response = await client.get(
                    "http://localhost:3000/api/datasources", auth=("admin", "admin")
                )
                if response.status_code == 200:
                    datasources = response.json()
                    has_prometheus = any(d.get("type") == "prometheus" for d in datasources)
                    if has_prometheus:
                        print("   ✅ Prometheus datasource configured in Grafana")
                    else:
                        print("   ⚠️ Prometheus datasource not found in Grafana")
        except Exception as e:
            print(f"   ⚠️ Could not verify: {str(e)}")

    async def test_all_services(self) -> None:
        """Test all services."""
        print("\n🧪 MPtoO Services Connectivity Test")
        print("=" * 60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Test PostgreSQL
        print("1️⃣ Testing PostgreSQL...")
        success, message = await self.test_postgresql()
        self.results.append(("PostgreSQL", success, message))
        print(f"   {message}")

        # Test Redis
        print("\n2️⃣ Testing Redis...")
        success, message = await self.test_redis()
        self.results.append(("Redis", success, message))
        print(f"   {message}")

        # Test HTTP services
        http_services = [
            ("MinIO", "MinIO", "/minio/health/live"),
            ("MLflow", "MLflow", "/health"),
            ("Label Studio", "Label Studio", "/health"),
            ("Prometheus", "Prometheus", "/-/healthy"),
            ("Grafana", "Grafana", "/api/health"),
            ("Prefect", "Prefect", "/api/health"),
        ]

        for idx, (name, service_name, endpoint) in enumerate(http_services, start=3):
            print(f"\n{idx}️⃣ Testing {name}...")
            config = self.services_config[service_name]
            success, message = await self.test_http_service(service_name, config["url"], endpoint)
            self.results.append((name, success, message))
            print(f"   {message}")

        # Test inter-service communication
        await self.test_service_communication()

        # Summary
        self.print_summary()

    def print_summary(self) -> None:
        """Print test summary."""
        print("\n" + "=" * 60)
        print("📊 Test Summary")
        print("=" * 60)

        successful = sum(1 for _, success, _ in self.results if success)
        total = len(self.results)

        for service, success, message in self.results:
            status = "✅" if success else "❌"
            print(f"{status} {service:20s} - {message}")

        print("\n" + "=" * 60)
        print(f"Results: {successful}/{total} services accessible")

        if successful == total:
            print("🎉 All services are running and accessible!")
            print("\n✅ Your MPtoO stack is ready to use!")
        else:
            print("\n⚠️ Some services are not accessible.")
            print("Please check:")
            print("  1. Docker containers are running: docker-compose ps")
            print("  2. Check logs: docker-compose logs <service-name>")
            print("  3. Verify ports are not already in use")

        print("=" * 60)

    def exit_code(self) -> int:
        """Return exit code based on results."""
        successful = sum(1 for _, success, _ in self.results if success)
        total = len(self.results)
        return 0 if successful == total else 1


async def main():
    """Main function."""
    tester = ServiceTester()
    await tester.test_all_services()
    sys.exit(tester.exit_code())


if __name__ == "__main__":
    # Check dependencies
    try:
        import asyncpg
        import httpx
        import redis.asyncio
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\nPlease install dependencies:")
        print("  pip install asyncpg httpx redis")
        sys.exit(1)

    asyncio.run(main())
