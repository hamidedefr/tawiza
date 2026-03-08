#!/bin/bash
# Start MPtoO v2 Platform

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 Starting MPtoO v2 Platform${NC}"

# Check .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️ No .env file found, copying from .env.example${NC}"
    cp .env.example .env
fi

# Parse arguments
PROFILE=""
if [ "$1" == "--ml" ]; then
    PROFILE="--profile ml"
    echo -e "${GREEN}📦 Including ML services (Label Studio)${NC}"
fi
if [ "$1" == "--crawler" ]; then
    PROFILE="--profile crawler"
    echo -e "${GREEN}🕷️ Including Crawler services (Skyvern)${NC}"
fi
if [ "$1" == "--full" ]; then
    PROFILE="--profile ml --profile crawler"
    echo -e "${GREEN}🌟 Starting full stack${NC}"
fi

# Start services
echo -e "${GREEN}📦 Starting core services...${NC}"
docker compose -f docker-compose.mptoo-v2.yml $PROFILE up -d

echo ""
echo -e "${GREEN}✅ MPtoO v2 Platform Started!${NC}"
echo ""
echo "📊 Services:"
echo "  • Evaluator: http://localhost:8511"
echo "  • Admin:     http://localhost:8512"
echo "  • ML:        http://localhost:8513"
echo "  • API:       http://localhost:8010/docs"
echo "  • Qdrant:    http://localhost:6333"
echo "  • MinIO:     http://localhost:9003 (API: 9002)"
echo ""
echo "🔧 Commands:"
echo "  • Stop:  docker compose -f docker-compose.mptoo-v2.yml down"
echo "  • Logs:  docker compose -f docker-compose.mptoo-v2.yml logs -f"
