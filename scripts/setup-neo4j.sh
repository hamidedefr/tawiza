#!/bin/bash
# scripts/setup-neo4j.sh - Deploy Neo4j for TAJINE MVP

set -e

echo "=== Deploying Neo4j for TAJINE MVP ==="

# Option 1: Docker (si disponible)
if command -v docker &> /dev/null; then
    echo "Using Docker deployment..."

    # Stop and remove existing container if any
    docker stop neo4j-tajine 2>/dev/null || true
    docker rm neo4j-tajine 2>/dev/null || true

    docker run -d \
        --name neo4j-tajine \
        -p 7474:7474 \
        -p 7687:7687 \
        -e NEO4J_AUTH=neo4j/tajine2024 \
        -e NEO4J_PLUGINS='["apoc"]' \
        -v neo4j-data:/data \
        neo4j:5.15.0

    echo "Neo4j deployed via Docker"
    echo "Web UI: http://localhost:7474"
    echo "Bolt: bolt://localhost:7687"
else
    echo "Docker not found. Please install Docker or deploy Neo4j manually."
    exit 1
fi

# Health check with retry loop
echo "Waiting for Neo4j to be ready..."
TIMEOUT=30
ELAPSED=0
until curl -sf http://localhost:7474 > /dev/null 2>&1; do
    if [ $ELAPSED -ge $TIMEOUT ]; then
        echo "ERROR: Neo4j failed to start within ${TIMEOUT}s" >&2
        docker logs neo4j-tajine >&2
        exit 1
    fi
    sleep 2
    ELAPSED=$((ELAPSED + 2))
done

echo "Neo4j is ready!"
