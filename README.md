```
 ████████╗ █████╗ ██╗    ██╗██╗███████╗ █████╗
 ╚══██╔══╝██╔══██╗██║    ██║██║╚══███╔╝██╔══██╗
    ██║   ███████║██║ █╗ ██║██║  ███╔╝ ███████║
    ██║   ██╔══██║██║███╗██║██║ ███╔╝  ██╔══██║
    ██║   ██║  ██║╚███╔███╔╝██║███████╗██║  ██║
    ╚═╝   ╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝╚══════╝╚═╝  ╚═╝
```

# Tawiza — Intelligence territoriale propulsee par l'IA

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

> Parce que scraper l'INSEE a la main, c'est so 2020.

**Tawiza** est une plateforme open source d'intelligence economique et territoriale francaise. Elle analyse les entreprises, les territoires et les dynamiques economiques en s'appuyant sur 15+ APIs gouvernementales et des agents IA cognitifs.

> **Tawiza** (ⵜⴰⵡⵉⵣⴰ) — mot amazigh signifiant *entraide collective*. Parce que l'intelligence economique, c'est mieux a plusieurs.

---

## Pourquoi Tawiza ?

- **Les donnees publiques francaises sont un tresor**... disperse sur 15 APIs differentes, avec 15 formats differents, et 15 facons de paginer. On a fait le sale boulot pour vous.
- **L'IA sans donnees reelles, c'est de la fiction**. Tawiza ne triche pas : zero mock, zero donnees synthetiques. Tout vient d'APIs gouvernementales en production.
- **Analyser un territoire, ca ne devrait pas prendre 3 semaines**. Un agent IA cognitif (TAJINE) decompose votre question, collecte les donnees, et synthetise — pendant que vous prenez un cafe.
- **Self-hostable, forkable, hackable**. Votre intelligence economique vous appartient.

---

## Fonctionnalites

### Agent TAJINE — Le cerveau

L'agent TAJINE suit le cycle **PPDSL** (Perceive-Plan-Delegate-Synthesize-Learn) avec 5 niveaux cognitifs :

| Niveau | Capacite | Exemple |
|--------|----------|---------|
| **Discovery** | Extraction factuelle | "Combien d'entreprises tech a Toulouse ?" |
| **Causal** | Analyse causale | "Pourquoi le secteur BTP recule en Occitanie ?" |
| **Scenario** | Simulation What-If | "Et si on doublait les subventions innovation ?" |
| **Strategy** | Recommandations | "Ou investir pour maximiser l'emploi ?" |
| **Theoretical** | Principes generaux | "Quels facteurs structurels expliquent l'attractivite ?" |

### Sources de donnees — 15+ APIs integrees

| Source | Type | Auth requise |
|--------|------|:------------:|
| **SIRENE** | Entreprises francaises (11M+) | Non |
| **BODACC** | Annonces legales | Non |
| **BOAMP** | Marches publics | Non |
| **INSEE Local** | Statistiques regionales | Oui (gratuit) |
| **France Travail** | Offres d'emploi | Oui (OAuth2) |
| **DVF** | Transactions immobilieres | Non |
| **BAN** | Geocodage adresses | Non |
| **RNA** | Associations | Non |
| **Subventions** | Aides territoriales | Non |
| **GDELT** | Evenements mondiaux | Non |
| **DBNomics** | Donnees economiques | Non |
| **CommonCrawl** | Archive web | Non |
| **PyTrends** | Tendances Google | Non |
| **RSS Enhanced** | News temps reel | Non |
| **Wikipedia** | Pageviews | Non |

### Dashboard — 15+ pages

- **Chat IA** — Posez vos questions en langage naturel (WebSocket temps reel)
- **Cockpit territorial** — Radar 6 axes, heatmaps, flux Sankey
- **Analytics** — Timeseries BODACC, repartition sectorielle, predictions
- **Investigation** — Cartographie des relations inter-entreprises (graphe)
- **Decisions** — Matrice d'impact, stakeholders RACI
- **Signaux** — Detection d'anomalies (ML)
- **Web Intelligence** — Crawling adaptatif de sources configurables
- **Departments** — Classement et detail par departement
- **Comparaison** — Benchmarking entre territoires
- **Fine-tuning** — Interface d'annotation (Label Studio)

### Analyse territoriale

- **6 axes** : Infrastructure, Capital humain, Innovation, Export, Investissement, Durabilite
- **Simulation Monte Carlo** + modelisation agent-based
- **Scoring multi-facteurs** avec inference causale (DoWhy)

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose

### En 5 commandes

```bash
# Cloner
git clone https://github.com/hamidedefr/tawiza.git && cd tawiza

# Services (PostgreSQL + Redis)
docker compose up -d db redis

# Backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env && alembic upgrade head
uvicorn src.interfaces.api.main:app --reload --port 8000

# Frontend (dans un autre terminal)
cd frontend && npm install && cp .env.local.example .env.local
npm run dev
```

Backend : http://localhost:8000/docs | Frontend : http://localhost:3000

### Avec Docker Compose (tout-en-un)

```bash
git clone https://github.com/hamidedefr/tawiza.git && cd tawiza
cp .env.example .env
docker compose up -d
```

### LLM local (optionnel)

```bash
# Installer Ollama (https://ollama.ai)
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull qwen2.5:7b           # Modele principal
ollama pull nomic-embed-text      # Embeddings
```

---

## Architecture

```
                    ┌──────────────────────────────────┐
                    │       Frontend (Next.js 14)       │
                    │   Dashboard · Chat · Analytics     │
                    └───────────────┬──────────────────┘
                                    │ REST + WebSocket
                    ┌───────────────▼──────────────────┐
                    │        API Layer (FastAPI)         │
                    │   Routes · Middleware · Auth       │
                    └───────────────┬──────────────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
           │                        │                        │
 ┌─────────▼─────────┐  ┌──────────▼──────────┐  ┌──────────▼──────────┐
 │   Application     │  │   Agent TAJINE      │  │   Data Sources      │
 │   Services        │  │   (Cycle PPDSL)     │  │   (15+ APIs)        │
 └─────────┬─────────┘  └──────────┬──────────┘  └──────────┬──────────┘
           │                        │                        │
 ┌─────────▼────────────────────────▼────────────────────────▼──────────┐
 │                        Infrastructure                                │
 │   PostgreSQL · Redis · Ollama · pgvector                            │
 └─────────────────────────────────────────────────────────────────────┘
```

L'architecture suit le pattern **hexagonal** (ports & adapters). Voir [docs/architecture.md](docs/architecture.md) pour les details.

---

## Tech Stack

| Couche | Technologies |
|--------|-------------|
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy (async), Alembic |
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS, shadcn/ui |
| **Visualisation** | Recharts, D3.js, Plotly |
| **Base de donnees** | PostgreSQL 17 + pgvector |
| **Cache** | Redis (multi-niveaux) |
| **LLM** | Ollama (local) avec HybridLLMRouter |
| **ML** | scikit-learn, PyMC, DoWhy |
| **Web Scraping** | Crawl4AI, Playwright |
| **Monitoring** | Prometheus, Grafana, Langfuse |
| **Tests** | pytest, pytest-asyncio |

---

## Configuration

Toute la configuration passe par des variables d'environnement. Voir [docs/configuration.md](docs/configuration.md) pour la reference complete.

Variables essentielles :

```bash
DATABASE_URL=postgresql+asyncpg://tawiza:changeme@localhost:5433/tawiza
REDIS_URL=redis://localhost:6380/0
OLLAMA_BASE_URL=http://localhost:11434    # Optionnel
SECRET_KEY=CHANGEZ_MOI_EN_PRODUCTION     # Obligatoire
```

> Les ports sont volontairement non-standard (5433, 6380, 3003) pour eviter les conflits. C'est un choix, pas un bug.

---

## Documentation

| Document | Description |
|----------|-------------|
| [Getting Started](docs/getting-started.md) | Installation detaillee |
| [Architecture](docs/architecture.md) | Structure du projet |
| [Configuration](docs/configuration.md) | Variables d'environnement |
| [Data Sources](docs/data-sources.md) | Catalogue des 15+ APIs |
| [API Reference](docs/api-reference.md) | Endpoints REST & WebSocket |
| [Self-Hosting](docs/self-hosting.md) | Guide de deploiement |
| [Contributing](CONTRIBUTING.md) | Guide de contribution |
| [Security](SECURITY.md) | Politique de securite |

---

## Contribuer

Les contributions sont les bienvenues ! Que ce soit un bug fix, une nouvelle source de donnees, ou une amelioration du dashboard.

```bash
# Fork, clone, branch
git checkout -b feat/ma-feature

# Coder, tester
pytest tests/ -v
ruff check src/

# PR !
```

Consultez le [guide de contribution](CONTRIBUTING.md) pour les details. Les issues [`good first issue`](https://github.com/hamidedefr/tawiza/labels/good%20first%20issue) sont un bon point de depart.

---

## Roadmap

- [ ] Internationalisation (i18n) du frontend
- [ ] API GraphQL en complement du REST
- [ ] Plugin system pour les sources de donnees communautaires
- [ ] Mode offline avec cache local des APIs
- [ ] Application mobile (React Native)
- [ ] Integration Jupyter Notebook pour l'analyse exploratoire

---

## Communaute

- [GitHub Discussions](https://github.com/hamidedefr/tawiza/discussions) — Questions, idees, retours
- [Issues](https://github.com/hamidedefr/tawiza/issues) — Bugs et feature requests

---

## License

[MIT](LICENSE) — Faites-en ce que vous voulez, mais gardez la mention.

---

<p align="center">
  <i>Fait avec du cafe, des donnees ouvertes, et une pointe d'obstination.</i>
  <br>
  <sub>L'intelligence territoriale pour tous — pas juste pour ceux qui ont le budget.</sub>
</p>
