#!/usr/bin/env python3
"""
Test script for pgvector client
Demonstrates usage and validates functionality
"""

import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np

from src.infrastructure.vector_store import PGVectorClient


async def main():
    """Test pgvector client functionality"""

    print("🧪 Testing PGVector Client")
    print("=" * 60)

    # Connection string - uses environment variable
    import os

    from dotenv import load_dotenv

    load_dotenv()
    password = os.getenv("DATABASE_PASSWORD", "WIN0SkfwqV9GNfLH8wFlJ7dsl0Vr83k0")
    dsn = f"postgresql://mptoo:{password}@localhost:5432/mptoo"
    print(f"Using password: {password[:5]}...{password[-5:]}")

    # Initialize client
    client = PGVectorClient(dsn, embedding_dim=768)
    await client.connect(min_size=5, max_size=10)

    try:
        # Test 1: Insert single embedding
        print("\n✅ Test 1: Insert single embedding")
        test_embedding = np.random.rand(768).tolist()
        row_id = await client.insert_embedding(
            document_id="test_doc_1",
            chunk_id="chunk_0",
            content="This is a test document for pgvector",
            embedding=test_embedding,
            metadata={"category": "test", "language": "en"},
            source="test_suite",
        )
        print(f"   Inserted row ID: {row_id}")

        # Test 2: Bulk insert
        print("\n✅ Test 2: Bulk insert 100 embeddings")
        bulk_data = [
            {
                "document_id": f"bulk_doc_{i}",
                "chunk_id": "chunk_0",
                "content": f"Bulk test document {i}",
                "embedding": np.random.rand(768).tolist(),
                "metadata": {"category": "bulk", "index": i},
                "source": "bulk_test",
            }
            for i in range(100)
        ]
        inserted = await client.bulk_insert(bulk_data, batch_size=50)
        print(f"   Inserted {inserted} rows")

        # Test 3: Search
        print("\n✅ Test 3: Semantic search")
        query_embedding = np.random.rand(768).tolist()
        results = await client.search(
            query_embedding=query_embedding, limit=5, metadata_filter={"category": "bulk"}
        )
        print(f"   Found {len(results)} results")
        for i, result in enumerate(results):
            print(f"   {i + 1}. {result.document_id} (distance: {result.distance:.4f})")

        # Test 4: Get by document ID
        print("\n✅ Test 4: Get by document ID")
        chunks = await client.get_by_document_id("test_doc_1")
        print(f"   Found {len(chunks)} chunks for 'test_doc_1'")

        # Test 5: Get statistics
        print("\n✅ Test 5: Database statistics")
        stats = await client.get_stats()
        print(f"   Total embeddings: {stats['total_embeddings']}")
        print(f"   Unique documents: {stats['unique_documents']}")
        print(f"   Unique sources: {stats['unique_sources']}")
        print(f"   Table size: {stats['table_size']}")

        # Test 6: Delete
        print("\n✅ Test 6: Delete by source")
        deleted = await client.delete_by_source("test_suite")
        print(f"   Deleted {deleted} rows")

        deleted = await client.delete_by_source("bulk_test")
        print(f"   Deleted {deleted} bulk rows")

        print("\n" + "=" * 60)
        print("✅ All tests passed!")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
