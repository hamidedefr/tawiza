# MPtoO-V2 Port Allocation Guide

**Last updated:** 2026-02-06
**Version:** 3.0.0

## Port Summary Table (Resolved)

| Service | Host Port | Container Port | Source File | Notes |
|---------|-----------|----------------|-------------|-------|
| **FastAPI Backend** | 8000 | 8000 | docker-compose.yml (commented) | Main API |
| **FastAPI (Docker)** | 8010 | 8000 | docker-compose.mptoo-v2.yml | Containerized API |
| **Next.js Frontend** | 3000 | - | local dev | `npm run dev` |
| **Reflex Frontend** | 3001 | 3001 | docker-compose.openmanus.yml | OpenManus UI |
| **PostgreSQL** | 5433 | 5432 | docker-compose.yml | **Non-standard** |
| **Redis** | 6380 | 6379 | docker-compose.yml | **Non-standard** |
| **MinIO API** | 9002 | 9000 | docker-compose.yml | Avoid Portainer conflict |
| **MinIO Console** | 9003 | 9001 | docker-compose.yml | |
| **MLflow** | 5001 | 5000 | docker-compose.yml | Avoid Flask/AirPlay conflict |
| **Label Studio** | 8082 | 8080 | docker-compose.yml | |
| **Prometheus** | 9090 | 9090 | docker-compose.yml | |
| **Grafana** | 3003 | 3000 | docker-compose.yml | **Avoid Next.js conflict** |
| **Prefect** | 4200 | 4200 | docker-compose.yml | |
| **ChromaDB** | 8001 | 8000 | docker-compose.yml | Vector DB |
| **vLLM** | 8002 | - | .env | **Avoid ChromaDB conflict** |
| **Reflex Backend** | 8004 | 8001 | docker-compose.openmanus.yml | **Avoid ChromaDB conflict** |
| **Skyvern** | 8501 | 8501 | docker-compose.yml | |
| **Ollama** | 11434 | 11434 | local/docker | LLM inference |
| **Langfuse** | 3150 | 3000 | docker-compose.mptoo-v2.yml | **Avoid Loki conflict** |
| **Qdrant** | 6333 | 6333 | docker-compose.mptoo-v2.yml | |
| **Qdrant gRPC** | 6334 | 6334 | docker-compose.mptoo-v2.yml | |
| **OpenManus Core** | 8085 | 8085 | docker-compose.openmanus.yml | |
| **Streamlit Evaluator** | 8511 | 8501 | docker-compose.mptoo-v2.yml | |
| **Streamlit Admin** | 8512 | 8501 | docker-compose.mptoo-v2.yml | |
| **Streamlit ML** | 8513 | 8501 | docker-compose.mptoo-v2.yml | |
| **OTEL Collector** | 4317 | 4317 | .env | Telemetry |
| **Evidently** | 8080 | 8080 | .env | ML monitoring |

## Conflicts Resolved (v3.0.0)

### 1. PostgreSQL: 5432 -> 5433
- **Problem:** `.env` disait `localhost:5432` mais docker-compose mappait `5433:5432`
- **Fix:** `.env` DATABASE_URL mis a jour vers port 5433
- **Fichiers:** `.env`, `.env.example`

### 2. Redis: 6379 -> 6380
- **Problem:** `.env` disait `localhost:6379` mais docker-compose mappait `6380:6379`
- **Fix:** `.env` REDIS_URL mis a jour vers port 6380
- **Fichiers:** `.env`, `.env.example`

### 3. vLLM: 8001 -> 8002 (conflit 3-way)
- **Problem:** Port 8001 partage entre ChromaDB, vLLM, et Reflex Backend
- **Fix:** vLLM deplace vers 8002, Reflex Backend vers 8004
- **Fichiers:** `.env`, `.env.example`, `docker-compose.openmanus.yml`

### 4. Grafana: 3000 -> 3003
- **Problem:** Port 3000 partage entre Next.js frontend et Grafana
- **Fix:** Grafana deplace vers 3003
- **Fichiers:** `.env`, `.env.example`, `docker-compose.yml`, `docker-compose.openmanus.yml`

### 5. Langfuse: 3100 -> 3150
- **Problem:** Port 3100 utilisé par Loki, NEXTAUTH_URL inconsistant avec .env
- **Fix:** Langfuse deplace vers 3150, NEXTAUTH_URL corrige
- **Fichiers:** `docker-compose.mptoo-v2.yml`

## Modes de Developpement

### Standard (dev local)
Ports necessaires: 8000, 3000, 5433, 6380, 11434
```bash
# Backend + Frontend + DB + Cache + LLM
make docker-up   # PostgreSQL, Redis, MinIO, etc.
make run          # FastAPI sur :8000
cd frontend && npm run dev  # Next.js sur :3000
```

### Minimal (backend seul)
Ports necessaires: 8000, 5433, 6380
```bash
docker-compose up -d postgres redis
make run
```

### Docker complet
Tous les ports du tableau ci-dessus
```bash
docker-compose up -d
docker-compose -f docker/docker-compose.mptoo-v2.yml up -d
```

## Verification Rapide

```bash
# Verifier tous les ports
make check-ports

# Verifier les ports a risque seulement
./scripts/check-ports.sh --conflicts

# Sante des services
make health-check

# Diagnostic complet
make diagnose
```

## Reference Rapide URLs

```bash
# Applications
API:             http://localhost:8000
API Docs:        http://localhost:8000/docs
Frontend:        http://localhost:3000
Grafana:         http://localhost:3003     (admin/admin)
MLflow:          http://localhost:5001
MinIO Console:   http://localhost:9003
Label Studio:    http://localhost:8082
Langfuse:        http://localhost:3150
Prefect:         http://localhost:4200

# Infrastructure
PostgreSQL:      localhost:5433
Redis:           localhost:6380
ChromaDB:        http://localhost:8001
Ollama:          http://localhost:11434
Prometheus:      http://localhost:9090
```

## Conventions de Ports

| Plage | Usage |
|-------|-------|
| 3000-3999 | UI et dashboards (Next.js, Grafana, Langfuse) |
| 4000-4999 | Orchestration et telemetrie (Prefect, OTEL) |
| 5000-5999 | ML et tracking (MLflow, PostgreSQL) |
| 6000-6999 | Cache et vector DB (Redis, Qdrant) |
| 8000-8999 | Applications et API (FastAPI, ChromaDB, vLLM, Label Studio) |
| 9000-9999 | Infrastructure (MinIO, Prometheus) |
| 11000+ | Services externes (Ollama) |
