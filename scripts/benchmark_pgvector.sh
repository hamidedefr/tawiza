#!/bin/bash
# Benchmark pgvector performance
# Tests insert and search performance with real data

set -e

echo "🎯 PGVector Performance Benchmark"
echo "=================================="
echo ""

# Test 1: Insert performance
echo "Test 1: Bulk insert 1000 random vectors..."
START=$(date +%s%3N)

docker exec mptoo-postgres psql -h 127.0.0.1 -U mptoo -d mptoo -c "
DO \$\$
DECLARE
    i INT;
BEGIN
    FOR i IN 1..1000 LOOP
        INSERT INTO embeddings (document_id, chunk_id, content, embedding, metadata)
        VALUES (
            'bench_doc_' || i,
            'chunk_0',
            'Benchmark document ' || i,
            array_fill(random()::real, ARRAY[768])::vector,
            '{\"category\": \"benchmark\"}'::jsonb
        )
        ON CONFLICT (document_id, chunk_id) DO NOTHING;
    END LOOP;
END \$\$;
" > /dev/null 2>&1

END=$(date +%s%3N)
INSERT_TIME=$((END - START))

echo "✅ Inserted 1000 vectors in ${INSERT_TIME}ms"
echo ""

# Test 2: Search performance
echo "Test 2: Search performance (50 queries)..."

TOTAL_TIME=0
for j in {1..50}; do
    START=$(date +%s%3N)

    docker exec mptoo-postgres psql -h 127.0.0.1 -U mptoo -d mptoo -c "
    SELECT document_id, embedding <=> array_fill(random()::real, ARRAY[768])::vector as distance
    FROM embeddings
    WHERE metadata->>'category' = 'benchmark'
    ORDER BY distance
    LIMIT 10;
    " > /dev/null 2>&1

    END=$(date +%s%3N)
    QUERY_TIME=$((END - START))
    TOTAL_TIME=$((TOTAL_TIME + QUERY_TIME))
done

AVG_QUERY_TIME=$((TOTAL_TIME / 50))
QPS=$(awk "BEGIN {printf \"%.1f\", 1000/$AVG_QUERY_TIME}")

echo "✅ Average query time: ${AVG_QUERY_TIME}ms"
echo "✅ Queries per second (QPS): ${QPS}"
echo ""

# Test 3: Statistics
echo "Test 3: Database statistics..."
docker exec mptoo-postgres psql -h 127.0.0.1 -U mptoo -d mptoo -c "
SELECT * FROM embedding_stats;
"

echo ""
echo "=================================="
echo "📊 Performance Summary"
echo "=================================="
echo "Insert 1000 vectors: ${INSERT_TIME}ms"
echo "Average search time: ${AVG_QUERY_TIME}ms"
echo "QPS: ${QPS}"
echo ""

# Cleanup
echo "Cleaning up benchmark data..."
docker exec mptoo-postgres psql -h 127.0.0.1 -U mptoo -d mptoo -c "
DELETE FROM embeddings WHERE metadata->>'category' = 'benchmark';
" > /dev/null 2>&1

echo "✅ Benchmark complete!"
