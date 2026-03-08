#!/bin/bash

# Script de test de connectivité des services MPtoO
# Version simplifiée en bash (sans dépendances Python)

set -e

echo "🧪 MPtoO Services Connectivity Test (Bash Version)"
echo "================================================================="
date
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0

# Function to test service
test_service() {
    local name=$1
    local host=$2
    local port=$3
    local type=$4

    echo -n "Testing $name... "

    if [ "$type" == "tcp" ]; then
        # Test TCP connection
        if timeout 3 bash -c "cat < /dev/null > /dev/tcp/$host/$port" 2>/dev/null; then
            echo -e "${GREEN}✅ Port $port accessible${NC}"
            ((PASSED++))
            return 0
        else
            echo -e "${RED}❌ Port $port not accessible${NC}"
            ((FAILED++))
            return 1
        fi
    elif [ "$type" == "http" ]; then
        # Test HTTP endpoint
        if curl -f -s -o /dev/null -m 5 "$host"; then
            echo -e "${GREEN}✅ HTTP accessible${NC}"
            ((PASSED++))
            return 0
        else
            echo -e "${RED}❌ HTTP not accessible${NC}"
            ((FAILED++))
            return 1
        fi
    fi
}

# Test PostgreSQL
test_service "PostgreSQL" "localhost" "5432" "tcp"

# Test Redis
test_service "Redis" "localhost" "6379" "tcp"

# Test MinIO
test_service "MinIO API" "http://localhost:9000/minio/health/live" "" "http"
test_service "MinIO Console" "localhost" "9001" "tcp"

# Test MLflow
test_service "MLflow" "http://localhost:5000/health" "" "http"

# Test Label Studio
test_service "Label Studio" "http://localhost:8080/health" "" "http"

# Test Prometheus
test_service "Prometheus" "http://localhost:9090/-/healthy" "" "http"

# Test Grafana
test_service "Grafana" "http://localhost:3000/api/health" "" "http"

# Test Prefect
test_service "Prefect" "http://localhost:4200/api/health" "" "http"

# Summary
echo ""
echo "================================================================="
echo "📊 Test Summary"
echo "================================================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

TOTAL=$((PASSED + FAILED))

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All services are accessible!${NC}"
    echo "✅ Your MPtoO stack is ready to use!"
    exit 0
else
    echo -e "${YELLOW}⚠️ Some services are not accessible.${NC}"
    echo ""
    echo "Troubleshooting steps:"
    echo "  1. Check if containers are running:"
    echo "     docker-compose ps"
    echo ""
    echo "  2. Check service logs:"
    echo "     docker-compose logs <service-name>"
    echo ""
    echo "  3. Restart services:"
    echo "     docker-compose down && docker-compose up -d"
    exit 1
fi
