# Benchmark Outils de Crawling Open Source

> Pour le projet OpenClaw - Detection de micro-signaux territoriaux
> Date: 2026-02-07

---

## Tableau Comparatif Final

| Critere | Scrapy | Crawl4AI | Crawlee Python | Firecrawl (self-host) | Trafilatura | Scrapling |
|---------|--------|----------|----------------|----------------------|-------------|-----------|
| **Stars GitHub** | 59.6k | 59.6k | 8k | 70k | 4.8k | 8.5k |
| **Version** | 2.14.1 | 0.8.0 | 1.3.1 | 2.8.0 | 2.0.0 | 0.3.x |
| **Maturite** | 10+ ans | 1 an | 5 mois v1 | 2 ans | 4 ans | 1 an |
| **License** | BSD | Apache 2.0 | Apache 2.0 | AGPL-3.0 | Apache/GPL | BSD-3 |
| **Setup** | 4/5 | 4/5 | 4/5 | 2/5 | **5/5** | 4/5 |
| **Qualite extraction FR** | 2/5 | 4/5 | 2/5 | 4/5 | **5/5** | 2/5 |
| **Sortie LLM-ready** | 2/5 | **5/5** | 2/5 | **5/5** | 4/5 | 1/5 |
| **Sites JS/SPA** | 4/5 | 4/5 | **5/5** | 4/5 | 1/5 | 4/5 |
| **Anti-bot** | 2/5 | 2/5 | **4/5** | 2/5 (self) | 1/5 | **4/5** |
| **PostgreSQL** | 4/5 | 2/5 | **5/5** | 3/5 | 4/5 | 4/5 |
| **Integration spaCy** | 4/5 | 2/5 | 4/5 | 3/5 | **5/5** | 4/5 |
| **Scalabilite 50-100 src** | **5/5** | 3/5 | 4/5 | 3/5 | **5/5** | 2/5 |
| **Scheduling integre** | 1/5 | 1/5 | 1/5 | 1/5 | 1/5 | 1/5 |
| **Detection changements** | 1/5 | 1/5 | 1/5 | **5/5** (cloud) | 1/5 | 3/5 |
| **Maintenance/risque** | **5/5** | 3/5 | 4/5 | **5/5** | 4/5 | 3/5 |
| **Courbe apprentissage** | 3/5 | 4/5 | 4/5 | **5/5** | **5/5** | 4/5 |
| **SCORE TOTAL** | **3.2** | **3.0** | **3.4** | **3.0** | **3.5** | **2.8** |

---

## Recommandation

### Combo gagnant : Trafilatura + Crawlee Python

```
Trafilatura (extraction principale, 90% des sources)
     +
Crawlee Python AdaptivePlaywrightCrawler (sites JS/anti-bot, 10%)
     +
spaCy fr_core_news_lg (NER francais)
     +
PostgreSQL (stockage unifie)
```

### Pourquoi ce combo ?

| Composant | Role | Justification |
|-----------|------|---------------|
| **Trafilatura** | Extraction texte + decouverte URLs | Valide academiquement sur texte FR (F1=0.958), leger, RSS/sitemap/spider integres, zero infra |
| **Crawlee Python** | Sites JS et proteges | AdaptivePlaywrightCrawler unique (auto HTTP/browser), PostgreSQL natif, anti-bot Camoufox, asyncio |
| **spaCy** | NER territorial | Modeles FR entraines sur presse, extraction communes/orgas/personnes |
| **PostgreSQL** | Stockage signaux | Deja dans votre stack (port 5433), JSONB pour entites, pgvector pour embeddings |

---

## Analyse Detaillee par Outil

### 1. Scrapy (59.6k stars) - Le veteran industriel

**Forces :**
- Ecosysteme le plus riche (scrapy-playwright, scrapy-redis, spidermon, scrapy-poet)
- Pipelines structurees (Item -> NLP Pipeline -> DB Pipeline)
- Distribue via scrapy-redis (votre Redis port 6380)
- Documentation excellente, 10+ ans de maturite
- Scalabilite prouvee pour 100+ sources

**Faiblesses :**
- Base Twisted (pas asyncio natif) - integration complexe avec libs modernes
- Pas d'extraction automatique de contenu - il faut ecrire des selecteurs par site
- Pas de rendering JS natif (besoin scrapy-playwright)
- Pas de scheduling integre
- Courbe d'apprentissage (Spider, Item, Pipeline, Middleware)
- Anti-bot faible sans proxy externe

**Verdict :** Excellent framework industriel mais trop lourd pour notre besoin. On n'a pas besoin de crawl distribue massif mais de bonne extraction de contenu francais.

---

### 2. Crawl4AI (59.6k stars) - Le nouveau oriente LLM

**Forces :**
- Sortie Markdown exceptionnelle (raw, fit, with_citations)
- Extraction LLM native (schema Pydantic, provider-agnostic via LiteLLM)
- Compatible vLLM/Ollama local (pointe vers votre port 8002)
- Deep crawl BFS/DFS avec crash recovery
- MemoryAdaptiveDispatcher pour gestion RAM
- Docker avec API REST + playground

**Faiblesses :**
- Pas de PostgreSQL integre - pipeline manuelle
- Pas de scheduling, pas de deduplication inter-sessions
- Lourd en memoire (Chromium : 100-300MB par tab)
- Single maintainer (@unclecode) - bus factor 1
- API instable entre versions (breaking changes v0.4 -> v0.8)
- Pas de detection de changements

**Verdict :** Excellent pour le RAG/LLM mais overkill si on fait la detection de signaux avec spaCy. Le markdown LLM-ready est top mais on a besoin de texte brut pour le NER.

---

### 3. Crawlee Python (8k stars) - Le moderne asyncio

**Forces :**
- **AdaptivePlaywrightCrawler** : auto-switch HTTP/browser par page (unique!)
- PostgreSQL natif (`SqlStorageClient` via asyncpg)
- Anti-bot en couches : ImpitHttpClient (TLS Rust) + fingerprints + Camoufox
- Request queue persistante avec deduplication
- asyncio natif - integration directe avec libs Python modernes
- Back par Apify (entreprise financee) - faible risque d'abandon

**Faiblesses :**
- v1.0 depuis seulement sept 2025 (5 mois de maturite v1)
- Ecosysteme plus petit que Scrapy
- Documentation encore en construction
- Pas de scheduling integre
- RAM haute avec gros pools de proxy (issue #895)
- Pas d'extraction automatique de contenu

**Verdict :** Le meilleur choix pour les sites JS et proteges. L'AdaptivePlaywrightCrawler est parfait pour mixer sites statiques (mairies) et dynamiques (annonces immo).

---

### 4. Firecrawl (70k stars) - Le SaaS du crawling

**Forces :**
- Markdown output la meilleure qualite
- Change tracking (diff git entre crawls) - ideal pour surveiller mairies
- Extraction LLM avec schemas Pydantic
- Tres facile a utiliser (API simple)

**Faiblesses :**
- **AGPL-3.0** - licence copyleft, probleme si deploye comme service
- Self-hosted gourmand : 4 CPU / 8GB RAM minimum, + Redis + Playwright
- Features cles cloud-only : Fire-engine (anti-bot), change tracking, dashboard
- Self-hosted "pas production-ready" selon la communaute
- Cout cloud : 83-333$/mois pour 50-100 sources quotidiennes
- Deep research buggy en self-hosted (issue #1961)

**Verdict :** Excellent produit mais modele economique inadapte pour un projet perso. La licence AGPL et les features cloud-only eliminent le self-hosted serieux.

---

### 5. Trafilatura (4.8k stars) - L'extracteur academique

**Forces :**
- **Valide sur texte francais** (F1=0.958, publie en conference ACL)
- Extraction la plus propre pour le NER downstream
- RSS/Atom + Sitemaps + Spider integres
- `pip install trafilatura` - zero infra
- Deduplication, robots.txt, rate limiting integres
- Parallelisable avec `concurrent.futures`
- Sortie multi-format : JSON, CSV, XML, Markdown, TXT

**Faiblesses :**
- Pas de rendering JavaScript (HTML statique seulement)
- Pas d'anti-bot
- Pas de detection de changements integree
- Crawling basique (pas de logique complexe de navigation)
- Mainteneur unique (Adrien Barbaresi, academique)

**Verdict :** Le meilleur extracteur pour notre cas d'usage. Concu pour le francais, valide scientifiquement, zero overhead. Couvre 90% de nos sources (presse locale, sites mairies statiques).

---

### 6. Scrapling (8.5k stars) - L'adaptateur intelligent

**Forces :**
- **Adaptive scraping** : seleurs se reparent quand le site change
- StealthyFetcher (Cloudflare bypass, anti-fingerprint)
- Performance parsing 237x plus rapide que BeautifulSoup
- Leger quand utilise en mode fetcher simple

**Faiblesses :**
- Pas de crawling (fetcher seulement)
- Pas d'extraction automatique de contenu
- Necessite des selecteurs CSS par site (50-100 configs a maintenir)
- Pre-1.0, single maintainer
- Pas de decouverte d'URLs (RSS, sitemap)

**Verdict :** Le StealthyFetcher est utile comme complement pour les sites proteges, mais pas viable comme solution principale. Peut servir de fetcher pour Trafilatura sur les sites difficiles.

---

## Architecture Recommandee

```
[APScheduler / Celery Beat]
        |
        v
[Decouverte URLs]
  |-- Trafilatura feeds/sitemaps (presse, mairies)
  |-- Crawlee spider (sites complexes)
        |
        v
[Fetching + Extraction]
  |-- Trafilatura fetch+extract (90% sources : presse, mairies)
  |-- Crawlee AdaptivePlaywrightCrawler (10% : sites JS/anti-bot)
  |     + Trafilatura extract() sur le HTML rendu
        |
        v
[NLP Pipeline]
  |-- spaCy fr_core_news_lg (NER : LOC, ORG, PER)
  |-- Detection mots-cles signaux (ouverture, fermeture, etc.)
  |-- Sentiment analysis
        |
        v
[PostgreSQL :5433]
  |-- Table signals (source, commune, metric, value, date)
  |-- Table anomalies (croisement multi-sources)
  |-- JSONB pour entites et raw_data
        |
        v
[Detection Anomalies]
  |-- PyOD / STUMPY (series temporelles)
  |-- Croisement multi-sources
        |
        v
[Ollama (contextualisation) + Grafana :3003 (dashboard)]
```

### Combinaison fetching pour sites proteges

```python
from scrapling.fetchers import StealthyFetcher
import trafilatura

# Site protege : fetch avec Scrapling, extract avec Trafilatura
page = StealthyFetcher.fetch("https://site-protege.fr", headless=True)
result = trafilatura.extract(page.html_content, output_format="dict",
                              with_metadata=True, target_language="fr")
```

---

## Dependances Finales

```toml
[project]
name = "openclaw-collector"
version = "0.1.0"
requires-python = ">=3.11"

dependencies = [
    # Extraction principale
    "trafilatura>=2.0",

    # Crawling sites JS/anti-bot
    "crawlee[playwright,sql_postgres]>=1.3",

    # Fetching sites proteges (complement)
    "scrapling>=0.3",

    # NLP francais
    "spacy>=3.8",

    # Geographie
    "french-cities>=1.1",
    "geopy>=2.4",

    # Detection anomalies
    "pyod>=2.0",
    "stumpy>=1.14",

    # APIs francaises
    "pynsee[full]>=0.2",
    "httpx>=0.27",

    # Storage
    "sqlalchemy>=2.0",
    "asyncpg>=0.30",
    "psycopg2-binary>=2.9",

    # Scheduling
    "apscheduler>=3.10",

    # Data
    "pandas>=2.2",
    "pandera>=0.29",
]
```
