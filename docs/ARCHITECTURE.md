# TAJINE - Architecture Technique

**Date:** 2025-12-28
**Version:** MPtoO-V2

---

## 1. Vue d'Ensemble

TAJINE est une architecture multi-agents pour l'intelligence territoriale française. Le système combine un backend Python asynchrone, un frontend Next.js, et des services d'infrastructure (PostgreSQL, Redis, Ollama).

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND                                    │
│                        Next.js 14 (App Router)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   AI Chat   │  │   TAJINE    │  │  Analytics  │  │ Agent Live  │    │
│  │    Page     │  │  Dashboard  │  │    Page     │  │    Page     │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
│         │                │                │                │            │
│         └────────────────┴────────────────┴────────────────┘            │
│                                   │                                      │
│                          TAJINEContext                                   │
│                       (State Management)                                 │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │ HTTP/WebSocket
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              BACKEND                                     │
│                      FastAPI (Python 3.11+)                             │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     API Layer (interfaces/)                       │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │   │
│  │  │ REST Routes  │  │  WebSocket   │  │   Middleware         │   │   │
│  │  │ /api/v1/*    │  │  /ws         │  │ (Auth, CORS, Log)    │   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                   │                                      │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                 Application Layer (application/)                  │   │
│  │  ┌──────────────────┐  ┌──────────────────────────────────────┐ │   │
│  │  │ AgentOrchestrator│  │           Services                   │ │   │
│  │  │                  │  │ (TAJINEScheduler, AnalyticsService)  │ │   │
│  │  └──────────────────┘  └──────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                   │                                      │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │               Infrastructure Layer (infrastructure/)              │   │
│  │  ┌───────────────────────────────────────────────────────────┐  │   │
│  │  │                      TAJINE Agent                          │  │   │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────────┐  │  │   │
│  │  │  │ PPDSL   │ │Cognitive│ │ LLM     │ │    Learning     │  │  │   │
│  │  │  │ Engine  │ │ Levels  │ │ Router  │ │ (Trust/Data)    │  │  │   │
│  │  │  └─────────┘ └─────────┘ └─────────┘ └─────────────────┘  │  │   │
│  │  └───────────────────────────────────────────────────────────┘  │   │
│  │  ┌───────────────────────────────────────────────────────────┐  │   │
│  │  │                    Data Sources                            │  │   │
│  │  │  ┌────────┐ ┌────────┐ ┌───────┐ ┌─────┐ ┌────────────┐  │  │   │
│  │  │  │ SIRENE │ │ BODACC │ │ BOAMP │ │ BAN │ │Subventions │  │  │   │
│  │  │  └────────┘ └────────┘ └───────┘ └─────┘ └────────────┘  │  │   │
│  │  └───────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌──────────────┐          ┌──────────────┐          ┌──────────────┐
│  PostgreSQL  │          │    Redis     │          │    Ollama    │
│   (Data)     │          │   (Cache)    │          │    (LLM)     │
└──────────────┘          └──────────────┘          └──────────────┘
```

---

## 2. Couche Frontend

### 2.1 Structure des Fichiers

```
frontend/
├── app/                          # Next.js App Router
│   ├── layout.tsx                # Layout racine
│   ├── page.tsx                  # Redirect → /dashboard
│   ├── login/                    # Authentification
│   │   └── page.tsx
│   └── dashboard/
│       ├── layout.tsx            # DashboardLayout
│       ├── page.tsx              # Dashboard principal
│       ├── ai-chat/
│       │   └── page.tsx          # Chat TAJINE
│       ├── tajine/
│       │   └── page.tsx          # Dashboard territorial
│       ├── analytics/
│       │   └── page.tsx          # Métriques
│       └── agent-live/
│           └── page.tsx          # VNC viewer
│
├── components/
│   ├── chat/
│   │   └── ChatView.tsx          # Interface chat
│   ├── dashboard/
│   │   └── tajine/
│   │       ├── FranceMap.tsx     # Carte D3.js
│   │       └── charts/           # Graphiques Recharts
│   ├── layout/
│   │   └── index.tsx             # DashboardLayout
│   ├── navbar/
│   └── sidebar/
│
├── contexts/
│   ├── AuthContext.tsx           # Authentification
│   ├── TAJINEContext.tsx         # État TAJINE partagé
│   └── layout.tsx                # Sidebar state
│
├── hooks/
│   ├── use-tajine-websocket.ts   # WebSocket hook
│   └── use-department-data.ts    # SWR data fetching
│
└── lib/
    ├── api.ts                    # Client HTTP
    └── websocket.ts              # Client WebSocket
```

### 2.2 Flux de Données Frontend

```
┌─────────────────────────────────────────────────────────────────┐
│                        TAJINEContext                             │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐    │
│  │ currentChat │  │ analysisMode │  │ departmentStats     │    │
│  │ messages[]  │  │ "fast"|"full"│  │ Map<code, stats>    │    │
│  └──────┬──────┘  └──────┬───────┘  └──────────┬──────────┘    │
│         │                │                      │               │
└─────────┼────────────────┼──────────────────────┼───────────────┘
          │                │                      │
          ▼                ▼                      ▼
    ┌──────────┐    ┌──────────┐          ┌──────────┐
    │ ChatView │    │ ModeSwitch│          │FranceMap │
    │          │    │          │          │  Charts  │
    └──────────┘    └──────────┘          └──────────┘
```

### 2.3 Composants Clés

| Composant | Rôle | Dépendances |
|-----------|------|-------------|
| `ChatView` | Interface chat TAJINE | TAJINEContext, WebSocket |
| `FranceMap` | Carte France D3.js | department-stats API |
| `PPDSLProgress` | Visualisation cycle | WebSocket events |
| `DashboardLayout` | Layout avec sidebar | SidebarContext |

---

## 3. Couche Backend

### 3.1 Structure des Fichiers

```
src/
├── interfaces/                   # Couche API
│   └── api/
│       ├── main.py               # FastAPI app
│       ├── middleware/           # Auth, CORS
│       ├── v1/
│       │   ├── tajine/
│       │   │   └── routes.py     # Endpoints TAJINE
│       │   ├── auth/
│       │   │   └── routes.py     # Authentification
│       │   ├── analytics/
│       │   │   └── routes.py     # Métriques
│       │   └── conversations/
│       │       └── routes.py     # Historique
│       └── websocket/
│           ├── handlers.py       # TAJINEHandler
│           └── models.py         # Event schemas
│
├── application/                  # Couche Services
│   └── services/
│       ├── agent_orchestrator.py # Coordination agents
│       ├── tajine_scheduler.py   # Analyses planifiées
│       └── analytics_service.py  # Agrégation stats
│
└── infrastructure/               # Couche Infrastructure
    ├── agents/
    │   ├── tajine/               # Agent principal
    │   │   ├── tajine_agent.py   # TAJINEAgent class
    │   │   ├── llm_router.py     # HybridLLMRouter
    │   │   ├── planning.py       # PlanningEngine
    │   │   ├── cognitive/
    │   │   │   ├── synthesizer.py
    │   │   │   └── levels/
    │   │   │       ├── discovery.py
    │   │   │       ├── causal.py
    │   │   │       ├── scenario.py
    │   │   │       ├── strategy.py
    │   │   │       └── theoretical.py
    │   │   ├── learning/
    │   │   │   ├── trust_manager.py
    │   │   │   └── data_collector.py
    │   │   └── tools/
    │   ├── manus/                # Agent exécution
    │   └── browser/              # Automatisation web
    │
    ├── datasources/
    │   ├── adapters/
    │   │   ├── sirene.py
    │   │   ├── bodacc.py
    │   │   ├── boamp.py
    │   │   ├── ban.py
    │   │   └── subventions.py
    │   └── services/
    │       └── data_source_manager.py
    │
    ├── llm/
    │   ├── ollama_client.py
    │   └── prompt_templates.py
    │
    ├── persistence/
    │   ├── database.py
    │   ├── models/
    │   │   ├── user_model.py
    │   │   └── conversation_model.py
    │   └── repositories/
    │
    └── tools/
        └── registry.py           # ToolRegistry
```

### 3.2 Agent TAJINE

#### Architecture Interne

```
┌─────────────────────────────────────────────────────────────────┐
│                        TAJINEAgent                               │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    PPDSL Engine                           │  │
│  │                                                           │  │
│  │  ┌─────────┐   ┌─────────┐   ┌──────────┐               │  │
│  │  │PERCEIVE │ → │  PLAN   │ → │ DELEGATE │               │  │
│  │  │         │   │         │   │          │               │  │
│  │  │ Collect │   │Strategy │   │ Execute  │               │  │
│  │  │ Data    │   │ Select  │   │ Tools    │               │  │
│  │  └─────────┘   └─────────┘   └──────────┘               │  │
│  │       ↑                            │                      │  │
│  │       │                            ▼                      │  │
│  │  ┌─────────┐                ┌───────────┐                │  │
│  │  │  LEARN  │ ←───────────── │SYNTHESIZE │                │  │
│  │  │         │                │           │                │  │
│  │  │ Update  │                │  Fuse     │                │  │
│  │  │ Trust   │                │  Levels   │                │  │
│  │  └─────────┘                └───────────┘                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────┐  ┌───────────────────────────────────┐  │
│  │  HybridLLMRouter │  │       UnifiedSynthesizer          │  │
│  │                  │  │                                    │  │
│  │  LOCAL     ────┐ │  │  Discovery  ─┐                    │  │
│  │  STANDARD  ────┤ │  │  Causal     ─┤                    │  │
│  │  POWERFUL  ────┤ │  │  Scenario   ─┼──→ Fusion Score   │  │
│  │  MAXIMUM   ────┘ │  │  Strategy   ─┤                    │  │
│  │                  │  │  Theoretical─┘                    │  │
│  └──────────────────┘  └───────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────┐  ┌───────────────────────────────────┐  │
│  │   TrustManager   │  │        DataCollector              │  │
│  │                  │  │                                    │  │
│  │  tool_trust{}   │  │  success_traces[]                 │  │
│  │  autonomy_level │  │  preference_pairs[]               │  │
│  └──────────────────┘  └───────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

#### Cycle PPDSL Détaillé

```python
async def run_ppdsl_cycle(self, query: str, context: dict) -> TAJINEResponse:
    # PERCEIVE - Collecte des données pertinentes
    data = await self._perceive(query, context)

    # PLAN - Sélection de la stratégie
    plan = await self.planning_engine.create_plan(query, data)

    # DELEGATE - Exécution des outils
    results = []
    for step in plan.steps:
        tool = self.tool_registry.get(step.tool_name)
        result = await tool.execute(**step.params)
        results.append(result)

    # SYNTHESIZE - Fusion multi-niveaux
    synthesis = await self.synthesizer.synthesize(query, results)

    # LEARN - Mise à jour confiance
    await self.trust_manager.update(plan.steps, results)
    await self.data_collector.collect(query, synthesis, results)

    return TAJINEResponse(
        content=synthesis.response,
        cognitive_level=synthesis.level,
        confidence=synthesis.confidence,
        sources=synthesis.sources
    )
```

### 3.3 Niveaux Cognitifs

| Niveau | Fichier | Rôle | Output |
|--------|---------|------|--------|
| Discovery | `discovery.py` | Exploration initiale | Faits bruts, patterns |
| Causal | `causal.py` | Relations cause-effet | Graphe causal |
| Scenario | `scenario.py` | Projections futures | Scénarios probabilistes |
| Strategy | `strategy.py` | Recommandations | Actions prioritisées |
| Theoretical | `theoretical.py` | Modèles abstraits | Théories, lois |

### 3.4 LLM Router

```python
class HybridLLMRouter:
    TIER_MAPPING = {
        LLMTier.LOCAL: "qwen2.5:3b",
        LLMTier.STANDARD: "qwen2.5:14b",
        LLMTier.POWERFUL: "qwen2.5:32b",
        LLMTier.MAXIMUM: "qwen2.5:72b",
    }

    async def route(self, task: Task) -> LLMTier:
        if task.complexity < 0.3:
            return LLMTier.LOCAL
        elif task.complexity < 0.6:
            return LLMTier.STANDARD
        elif task.complexity < 0.8:
            return LLMTier.POWERFUL
        else:
            return LLMTier.MAXIMUM
```

---

## 4. Sources de Données

### 4.1 Adaptateurs

```
┌─────────────────────────────────────────────────────────────┐
│                   DataSourceManager                          │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ SIRENEAdapter│  │BODACCAdapter │  │ BOAMPAdapter │      │
│  │              │  │              │  │              │      │
│  │ search()     │  │ search()     │  │ search()     │      │
│  │ get_by_siret│  │ get_recent() │  │ get_tenders()│      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │               │
│         └─────────────────┼─────────────────┘               │
│                           ▼                                  │
│                    ┌──────────────┐                         │
│                    │    Redis     │                         │
│                    │   (Cache)    │                         │
│                    └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Protocole Adapter

```python
class DataSourceAdapter(Protocol):
    async def search(self, query: str, **filters) -> list[dict]:
        """Recherche générique."""
        ...

    async def get_by_id(self, id: str) -> dict | None:
        """Récupération par identifiant."""
        ...

    @property
    def source_name(self) -> str:
        """Nom de la source pour attribution."""
        ...
```

---

## 5. Système de Mémoire

### 5.1 Architecture Actuelle

```
┌─────────────────────────────────────────────────────────────┐
│                    Mémoire TAJINE                            │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Court Terme (Session)                    │  │
│  │                                                       │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │   Redis     │  │  Context    │  │   State     │  │  │
│  │  │   Cache     │  │   Window    │  │   Machine   │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Long Terme (Persistant)                  │  │
│  │                                                       │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │ PostgreSQL  │  │ trust.json  │  │training.json│  │  │
│  │  │Conversations│  │ Tool Scores │  │  SFT/DPO    │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              À Implémenter                            │  │
│  │                                                       │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │  pgvector   │  │   Neo4j     │  │  Feedback   │  │  │
│  │  │  Episodic   │  │   Graph     │  │    Loop     │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Trust Manager

```python
@dataclass
class TrustState:
    trust_score: float          # 0.0 - 1.0
    autonomy_level: str         # SUPERVISED | SEMI_AUTONOMOUS | AUTONOMOUS
    success_count: int
    failure_count: int
    tool_trust: dict[str, ToolTrust]

class TrustManager:
    AUTONOMY_THRESHOLDS = {
        "SUPERVISED": 0.0,
        "SEMI_AUTONOMOUS": 0.5,
        "AUTONOMOUS": 0.8,
    }

    async def update_after_execution(
        self,
        tool_name: str,
        success: bool,
        quality_score: float
    ) -> None:
        # Mise à jour trust par outil
        # Recalcul trust global
        # Ajustement autonomy_level
```

---

## 6. Communication

### 6.1 REST API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/tajine/analyze` | POST | Lancer analyse |
| `/api/v1/tajine/status` | GET | État agent |
| `/api/v1/tajine/department-stats` | GET | Stats départements |
| `/api/v1/conversations` | GET | Liste conversations |
| `/api/v1/analytics` | GET | Métriques globales |

### 6.2 WebSocket

```
┌────────────────────────────────────────────────────────────┐
│                    WebSocket /ws                            │
│                                                             │
│  Client                          Server                     │
│    │                               │                        │
│    │─── {"type": "subscribe",  ───→│                        │
│    │     "channel": "tajine"}      │                        │
│    │                               │                        │
│    │←── {"type": "ppdsl_update", ──│  TAJINEHandler         │
│    │     "phase": "DELEGATE",      │  broadcasts events     │
│    │     "progress": 60}           │                        │
│    │                               │                        │
│    │←── {"type": "analysis_done",──│                        │
│    │     "result": {...}}          │                        │
│    │                               │                        │
└────────────────────────────────────────────────────────────┘
```

### 6.3 Event Schema

```typescript
interface TAJINEEvent {
  type: 'ppdsl_update' | 'level_change' | 'analysis_done' | 'error';
  session_id: string;
  timestamp: number;
  payload: {
    phase?: 'PERCEIVE' | 'PLAN' | 'DELEGATE' | 'SYNTHESIZE' | 'LEARN';
    cognitive_level?: 'discovery' | 'causal' | 'scenario' | 'strategy' | 'theoretical';
    progress?: number;  // 0-100
    result?: TAJINEResponse;
    error?: string;
  };
}
```

---

## 7. Infrastructure

### 7.1 Services Docker

```yaml
services:
  backend:
    build: .
    ports: ["8000:8000"]
    depends_on: [postgres, redis, ollama]

  frontend:
    build: ./frontend
    ports: ["3000:3000"]

  postgres:
    image: postgres:15
    volumes: ["pgdata:/var/lib/postgresql/data"]

  redis:
    image: redis:7-alpine

  ollama:
    image: ollama/ollama
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]
```

### 7.2 Variables d'Environnement

```bash
# Backend
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/mptoo
REDIS_URL=redis://redis:6379/0
OLLAMA_URL=http://ollama:11434
SECRET_KEY=<random-secret>

# Optional monitoring
SENTRY_DSN=<sentry-dsn>
LANGFUSE_PUBLIC_KEY=<key>
LANGFUSE_SECRET_KEY=<secret>

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

---

## 8. Patterns et Conventions

### 8.1 Backend

```python
# Logging avec loguru
from loguru import logger
logger.info("Event", extra={"context": data})

# Async partout
async def fetch_data() -> list[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# Pydantic pour validation
class AnalysisRequest(BaseModel):
    query: str
    mode: Literal["fast", "complete"] = "fast"
    territory: str | None = None
```

### 8.2 Frontend

```typescript
// SWR pour data fetching
const { data, error, isLoading } = useSWR(
  '/api/tajine/department-stats',
  fetcher
);

// Context pour état partagé
const { currentAnalysis, setAnalysis } = useTAJINE();

// Tailwind + classes utilitaires
<div className="glass p-4 rounded-xl shadow-lg">
```

---

## 9. Sécurité

### 9.1 Authentification

- JWT tokens pour API
- Refresh tokens en cookies httpOnly
- CORS configuré pour domaines autorisés

### 9.2 Validation

- Pydantic pour toutes les entrées API
- Sanitization des queries SQL
- Rate limiting sur endpoints publics

---

## 10. Diagramme de Séquence Complet

```
User          Frontend       Backend        TAJINE         DataSources      LLM
  │              │              │              │                │            │
  │─ Query ─────→│              │              │                │            │
  │              │─ POST /analyze─→            │                │            │
  │              │              │─ run_ppdsl ──→               │            │
  │              │              │              │                │            │
  │              │              │              │── PERCEIVE ───→│            │
  │              │              │              │←── data ───────│            │
  │              │              │              │                │            │
  │              │              │              │── PLAN ────────────────────→│
  │              │              │              │←── strategy ───────────────│
  │              │              │              │                │            │
  │              │              │              │── DELEGATE ───→│            │
  │              │←─ WS: ppdsl_update ─────────│←── results ────│            │
  │              │              │              │                │            │
  │              │              │              │── SYNTHESIZE ─────────────→│
  │              │              │              │←── fusion ────────────────│
  │              │              │              │                │            │
  │              │              │              │── LEARN        │            │
  │              │              │←─ response ──│                │            │
  │              │←─ JSON ──────│              │                │            │
  │←─ Display ───│              │              │                │            │
```

---

*Architecture documentée par Claude Code (Opus 4.5)*
