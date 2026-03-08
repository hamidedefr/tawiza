# Architecture du Collector de Micro-Signaux

> Document de reference pour le projet OpenClaw/MoltBot
> Date: 2026-02-07

## Vision

Creer un systeme de collecte automatise qui detecte des **micro-signaux territoriaux** en croisant des donnees structurees (APIs open data) et non-structurees (crawling web) pour identifier des tendances emergentes avant qu'elles ne deviennent visibles.

```
Sources structurees (APIs)     Sources non-structurees (crawl)
  SIRENE, DVF, Sitadel...       Presse, annonces, mairies...
         |                              |
         v                              v
    Collectors API              Scrapy + Playwright
         |                              |
         |         +--------------------+
         v         v
    PostgreSQL (table unifiee signals)
              |
              v
    Detection anomalies (stats)
              |
              v
    Croisement multi-sources
              |
              v
    Ollama contextualise --> Alerte micro-signal
```

---

## 1. Projet de Reference : Signaux Faibles

> **Le projet le plus pertinent identifie.** Startup d'Etat (beta.gouv.fr) qui detecte les entreprises en difficulte via signaux faibles.

| | |
|---|---|
| **GitHub** | [signaux-faibles](https://github.com/signaux-faibles) |
| **Prediction (Python)** | [predictsignauxfaibles](https://github.com/signaux-faibles/predictsignauxfaibles) (archive) |
| **Plateforme (Go)** | [opensignauxfaibles](https://github.com/signaux-faibles/opensignauxfaibles) |
| **Concept** | Croise URSSAF + DIRECCTE + Banque de France + SIRENE |
| **Statut** | Archive mais code source disponible |

**Lecons a retenir :**
- Le croisement multi-sources est la cle (une source seule = bruit)
- Modele ML pour scorer la probabilite d'evenement
- Architecture orientee pipeline (collecte -> normalisation -> scoring -> alerte)

---

## 2. Stack Recommandee

### 2.1 Crawling & Scraping

| Outil | Stars | Usage | Pourquoi |
|-------|-------|-------|----------|
| **Scrapy** | ~59.6k | Crawling HTTP haute performance | Mature, plugins riches, production-ready |
| **Playwright** | ~70k | Sites JavaScript/SPA | Via `scrapy-playwright`, sites modernes mairies |
| **Crawl4AI** | ~51k | Crawling oriente LLM | Sortie Markdown propre pour analyse NLP |
| **Trafilatura** | ~5.3k | Extraction texte web | Meilleure qualite d'extraction, utilise par HuggingFace/Microsoft |
| **Newspaper4k** | ~913 | Extraction articles presse | 80+ langues, extraction titre/auteur/date/contenu |
| **Firecrawl** | ~70k | Monitoring changements web | Change tracking pour surveiller sites mairies/prefectures |
| **Scrapling** | trending | Scraping adaptatif | S'adapte quand les sites changent leur DOM |

#### Choix recommande pour le MVP

```
Scrapy (orchestration crawl)
  + scrapy-playwright (sites JS)
  + Trafilatura (extraction texte propre)
  + Newspaper4k (articles de presse)
```

### 2.2 Acces Donnees Francaises (APIs)

| Outil | GitHub | Usage |
|-------|--------|-------|
| **pynsee** | [InseeFrLab/pynsee](https://github.com/InseeFrLab/pynsee) | 150k+ series INSEE, donnees locales, SIRENE. Pas de cle API requise depuis v0.2.0 |
| **api_insee** | [ln-nicolas/api_insee](https://github.com/ln-nicolas/api_insee) | Requetes SIRENE specifiques (creation/radiation entreprises) |
| **datagouv_client** | [datagouv/datagouv_client](https://github.com/datagouv/datagouv_client) | Client officiel data.gouv.fr |
| **odsclient** | [smarie/python-odsclient](https://github.com/smarie/python-odsclient) | Portails OpenDataSoft (utilisee par centaines de collectivites) |
| **api-offres-emploi** | [etiennekintzler/api-offres-emploi](https://github.com/etiennekintzler/api-offres-emploi) | API France Travail (offres emploi par zone) |
| **dvf_as_api** | [cquest/dvf_as_api](https://github.com/cquest/dvf_as_api) | Transactions immobilieres DVF |

#### Sources de donnees et signaux detectables

| Source | API/Outil | Signal detecte | Frequence |
|--------|-----------|----------------|-----------|
| **SIRENE** | pynsee / api_insee | Creations/radiations entreprises par zone | Quotidien |
| **DVF** | dvf_as_api / bulk CSV | Prix immo, volumes transactions | Semestriel |
| **France Travail** | api-offres-emploi | Tension emploi, secteurs en mouvement | Quotidien |
| **Sitadel** | data.gouv.fr bulk | Permis construire = developpement futur | Mensuel |
| **INSEE local** | pynsee | Demographie, revenus, equipements | Annuel |
| **Presse locale** | Scrapy + Trafilatura | Ouvertures, fermetures, projets, crises | Quotidien |
| **Sites mairies** | Scrapy + Playwright | Deliberations, PLU, projets amenagement | Hebdo |
| **Annonces immo** | Scrapy | Prix, volumes, durees par zone | Quotidien |

### 2.3 Geographie & Referentiels

| Outil | GitHub | Usage |
|-------|--------|-------|
| **french-cities** | [tgrandje/french-cities](https://github.com/tgrandje/french-cities) | **CRITIQUE** : harmonisation codes commune/EPCI/dept, gestion COG multi-millesimes |
| **geopy** (BANFrance) | [geopy/geopy](https://github.com/geopy/geopy) | Geocodage adresses francaises via BAN |
| **pgeocode** | [symerio/pgeocode](https://github.com/symerio/pgeocode) | Geocodage offline par code postal |
| **france-geojson** | [gregoiredavid/france-geojson](https://github.com/gregoiredavid/france-geojson) | Contours GeoJSON toutes mailles administratives |
| **geo.api.gouv.fr** | API directe (pas de wrapper Python) | Recherche communes, codes INSEE, populations |

### 2.4 NLP Francais

| Outil | Usage | Pourquoi |
|-------|-------|----------|
| **spaCy** (fr_core_news_lg) | NER : extraction lieux, orgas, personnes | Production-ready, rapide, modeles francais entraines sur presse |
| **CamemBERT** | Comprehension fine du texte francais | SOTA francais, fine-tunable, NER via `Jean-Baptiste/camembert-ner` |
| **FlauBERT** | Alternative CamemBERT | Corpus plus diversifie |

**Recommandation :** spaCy pour le NER de base (extraction communes, organisations), CamemBERT si besoin de classification fine (sentiment, categorie de signal).

### 2.5 Detection d'Anomalies

| Outil | Stars | Usage | Pourquoi |
|-------|-------|-------|----------|
| **PyOD 2** | ~8.5k | Detection outliers multivariee | 45 algos, selection auto par LLM en v2 |
| **STUMPY** | ~4.1k | Matrix Profile (series temporelles) | Decouverte motifs + anomalies, GPU accelere |
| **ADTK** | ~1k | Detection anomalies series temporelles | Rule-based, explicable, leger |

**Recommandation :** PyOD pour anomalies multivariees (croisement sources), STUMPY pour patterns temporels.

### 2.6 Orchestration & Scheduling

| Outil | Stars | Usage | Quand |
|-------|-------|-------|-------|
| **APScheduler** | ~6k | Scheduler in-process | MVP / prototype |
| **Celery + Redis** | ~25k | File de taches distribuee | Production legere |
| **Prefect** | ~19.8k | Orchestration Pythonic | Production avec monitoring |
| **Airflow** | ~43.6k | DAGs complexes | Si besoin enterprise-grade |

**Recommandation :** APScheduler pour le MVP, migrer vers Prefect quand les pipelines se complexifient.

### 2.7 Qualite de Donnees

| Outil | Stars | Usage |
|-------|-------|-------|
| **Pandera** | ~3.5k | Validation schemas dans le code (Pandas/Polars) |
| **Great Expectations** | ~11.1k | Validation pipeline avec rapports auto |

---

## 3. Architecture Detaillee du Collector

### 3.1 Structure du projet

```
openclaw-collector/
├── collectors/
│   ├── base.py              # BaseCollector (classe abstraite)
│   ├── api/
│   │   ├── sirene.py        # Creations/radiations entreprises
│   │   ├── dvf.py           # Transactions immobilieres
│   │   ├── france_travail.py # Offres emploi
│   │   ├── sitadel.py       # Permis de construire
│   │   └── insee_local.py   # Stats locales INSEE
│   └── crawlers/
│       ├── presse_locale.py  # Spider presse regionale
│       ├── mairies.py        # Spider deliberations mairies
│       └── annonces_immo.py  # Spider annonces
├── processing/
│   ├── normalizer.py         # Normalisation commune/date/valeur
│   ├── geocoder.py           # Resolution geographique (french-cities)
│   ├── nlp.py                # Extraction entites (spaCy/CamemBERT)
│   └── dedup.py              # Deduplication
├── detection/
│   ├── anomaly.py            # Detection anomalies (PyOD/STUMPY)
│   ├── crossref.py           # Croisement multi-sources
│   └── scorer.py             # Score de confiance du signal
├── storage/
│   ├── models.py             # SQLAlchemy models
│   ├── repository.py         # Acces donnees
│   └── migrations/           # Alembic
├── scheduler/
│   ├── jobs.py               # Definitions des jobs
│   └── config.py             # Frequences par source
├── config/
│   ├── sources.yaml          # Configuration des sources
│   └── signals.yaml          # Definition des signaux recherches
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

### 3.2 Schema de donnees

```sql
-- Table unifiee des signaux collectes
CREATE TABLE signals (
    id              BIGSERIAL PRIMARY KEY,
    source          VARCHAR(50) NOT NULL,     -- 'sirene', 'dvf', 'presse', etc.
    source_url      TEXT,                      -- URL ou identifiant source
    collected_at    TIMESTAMPTZ DEFAULT NOW(),
    event_date      DATE,                      -- Date de l'evenement

    -- Localisation
    code_commune    VARCHAR(5),                -- Code INSEE commune
    code_epci       VARCHAR(9),                -- Code EPCI
    code_dept       VARCHAR(3),                -- Code departement
    latitude        DOUBLE PRECISION,
    longitude       DOUBLE PRECISION,

    -- Signal
    metric_name     VARCHAR(100) NOT NULL,     -- 'creation_entreprise', 'prix_m2', etc.
    metric_value    DOUBLE PRECISION,
    signal_type     VARCHAR(20),               -- 'positif', 'negatif', 'neutre'
    confidence      DOUBLE PRECISION DEFAULT 0.5,

    -- Donnees brutes
    raw_data        JSONB,
    extracted_text  TEXT,                       -- Texte extrait (pour crawl)
    entities        JSONB,                      -- Entites NER extraites

    -- Index
    CONSTRAINT idx_source_date UNIQUE (source, source_url, event_date)
);

CREATE INDEX idx_signals_commune ON signals(code_commune, event_date);
CREATE INDEX idx_signals_metric ON signals(metric_name, event_date);
CREATE INDEX idx_signals_dept ON signals(code_dept, event_date);

-- Table des anomalies detectees
CREATE TABLE anomalies (
    id              BIGSERIAL PRIMARY KEY,
    detected_at     TIMESTAMPTZ DEFAULT NOW(),
    code_commune    VARCHAR(5),

    -- Anomalie
    anomaly_type    VARCHAR(50),               -- 'spike', 'drop', 'trend_change'
    metrics         JSONB,                     -- Metriques impliquees
    sources         TEXT[],                    -- Sources concernees
    score           DOUBLE PRECISION,          -- Score de significativite

    -- Contexte
    description     TEXT,                      -- Description generee par LLM
    related_signals BIGINT[],                  -- IDs des signaux lies

    -- Statut
    status          VARCHAR(20) DEFAULT 'new', -- 'new', 'confirmed', 'dismissed'
    reviewed_at     TIMESTAMPTZ
);

-- Vue pour croisement rapide
CREATE VIEW signal_summary AS
SELECT
    code_commune,
    metric_name,
    date_trunc('week', event_date) AS semaine,
    COUNT(*) AS nb_signals,
    AVG(metric_value) AS avg_value,
    STDDEV(metric_value) AS stddev_value,
    array_agg(DISTINCT source) AS sources
FROM signals
GROUP BY code_commune, metric_name, date_trunc('week', event_date);
```

### 3.3 Detection de micro-signaux (algorithme)

```python
# Pseudo-code de la logique de croisement

def detect_micro_signals(code_commune: str, window_weeks: int = 12):
    """
    Detecte des micro-signaux par croisement multi-sources.
    Un micro-signal = anomalie sur 2+ sources convergentes.
    """

    # 1. Recuperer les anomalies recentes par source
    anomalies = {}
    for source in ['sirene', 'dvf', 'france_travail', 'presse', 'sitadel']:
        series = get_time_series(code_commune, source, window_weeks)
        anomalies[source] = detect_anomaly(series)  # PyOD / z-score

    # 2. Croisement : chercher les convergences
    micro_signals = []

    # Exemple : signal de declin
    if (anomalies['sirene'].get('radiations') == 'spike' and
        anomalies['presse'].get('sentiment') == 'negatif' and
        anomalies['dvf'].get('prix_m2') == 'drop'):
        micro_signals.append({
            'type': 'declin_territorial',
            'score': calculate_convergence_score(anomalies),
            'sources': ['sirene', 'presse', 'dvf'],
        })

    # Exemple : signal de dynamisme
    if (anomalies['sirene'].get('creations') == 'spike' and
        anomalies['sitadel'].get('permis') == 'spike' and
        anomalies['france_travail'].get('offres') == 'spike'):
        micro_signals.append({
            'type': 'dynamisme_territorial',
            'score': calculate_convergence_score(anomalies),
            'sources': ['sirene', 'sitadel', 'france_travail'],
        })

    # 3. Contextualisation LLM
    for signal in micro_signals:
        signal['description'] = llm_contextualize(signal, code_commune)

    return micro_signals
```

---

## 4. Plan d'Execution MVP

### Phase 1 : Fondations (semaine 1-2)
- [ ] Setup projet Python (`pyproject.toml`, structure)
- [ ] Schema PostgreSQL (tables signals + anomalies)
- [ ] BaseCollector avec rate limiting, retry, logging
- [ ] Integration `french-cities` pour resolution geographique

### Phase 2 : Premiers collectors API (semaine 3-4)
- [ ] Collector SIRENE (via `pynsee`)
- [ ] Collector France Travail (via API)
- [ ] Collector DVF (bulk CSV)
- [ ] Scheduler APScheduler pour collecte periodique

### Phase 3 : Premiers crawlers (semaine 5-6)
- [ ] Spider presse locale (Scrapy + Trafilatura)
- [ ] NLP extraction entites (spaCy fr)
- [ ] Pipeline normalisation + stockage

### Phase 4 : Detection (semaine 7-8)
- [ ] Detection anomalies par source (z-score + PyOD)
- [ ] Croisement multi-sources
- [ ] Dashboard Grafana signaux detectes
- [ ] Contextualisation Ollama

---

## 5. Dependances Python (pyproject.toml)

```toml
[project]
name = "openclaw-collector"
version = "0.1.0"
requires-python = ">=3.11"

dependencies = [
    # Crawling
    "scrapy>=2.14",
    "scrapy-playwright>=0.0.40",
    "trafilatura>=2.0",
    "newspaper4k>=0.9",

    # APIs francaises
    "pynsee[full]>=0.2",
    "api-insee>=1.0",
    "httpx>=0.27",

    # NLP
    "spacy>=3.8",

    # Geographie
    "french-cities>=1.1",
    "geopy>=2.4",

    # Detection anomalies
    "pyod>=2.0",
    "stumpy>=1.14",

    # Storage
    "sqlalchemy>=2.0",
    "alembic>=1.13",
    "psycopg2-binary>=2.9",

    # Scheduling
    "apscheduler>=3.10",

    # Data
    "pandas>=2.2",
    "pandera>=0.29",
]
```

---

## 6. Liens & References

### Projets de reference
- [Signaux Faibles](https://github.com/signaux-faibles) — Detection signaux faibles entreprises (beta.gouv.fr)
- [OpenFisca France](https://github.com/openfisca/openfisca-france) — Microsimulation fiscale
- [Gabarit](https://github.com/France-Travail/gabarit) — Templates projets data science (France Travail)

### These & recherche
- [Detection de signaux faibles (these 2023)](https://theses.hal.science/tel-04354383v1/file/112555_ABOU_JAMRA_2023_archivage.pdf)
- [Signaux faibles dans masses de donnees](https://www.openscience.fr/IMG/pdf/iste_ridows19v3n1_3.pdf)

### Portails de donnees
- [data.gouv.fr](https://www.data.gouv.fr) — Portail national open data
- [api.gouv.fr](https://api.gouv.fr) — Catalogue APIs publiques
- [api.insee.fr](https://api.insee.fr) — APIs INSEE
- [francetravail.io](https://francetravail.io/data/api) — APIs France Travail
- [app.dvf.etalab.gouv.fr](https://app.dvf.etalab.gouv.fr) — Visualisation DVF
