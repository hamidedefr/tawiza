# TAJINE Core Algorithm - Technical Reference

> **Version**: 1.0.0
> **Date**: 2025-12-25
> **Status**: Implementation Phase

This document provides a complete technical reference for the TAJINE core algorithm, documenting all implemented components, their APIs, and current status.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [DataHunter](#1-datahunter)
3. [Evaluator](#2-evaluator)
4. [CognitiveEngine](#3-cognitiveengine)
5. [TheoryBank](#4-theorybank)
6. [AutonomyManager](#5-autonomymanager)
7. [Implementation Status](#implementation-status)
8. [Roadmap](#roadmap)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           TAJINE Agent                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ DataHunter  │→ │  Evaluator  │→ │  Cognitive  │→ │  AutonomyManager    │ │
│  │             │  │             │  │   Engine    │  │                     │ │
│  │ • Bandit    │  │ • 3D Score  │  │ • 5 Levels  │  │ • Trust Score       │ │
│  │ • Hypothesis│  │ • KGValid   │  │ • Theories  │  │ • Human-in-Loop     │ │
│  │ • Graph Exp │  │ • AlphaTest │  │             │  │                     │ │
│  │ • Resilient │  │             │  │             │  │                     │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. DataHunter

**Location**: `src/infrastructure/agents/tajine/hunter/`

### Components

#### 1.1 SourceBandit (Multi-Armed Bandit)

**File**: `bandit.py`

```python
from src.infrastructure.agents.tajine.hunter import SourceBandit

bandit = SourceBandit(
    sources=["sirene", "bodacc", "boamp", "infogreffe"],
    exploration_rate=1.0  # UCB exploration parameter
)

# Select best sources based on learned rewards
selected = bandit.select(n=3)  # Returns: ["sirene", "boamp", "bodacc"]

# Update after fetch
bandit.update(source="sirene", reward=0.85)  # 0.0-1.0 based on quality
```

**Algorithm**: Upper Confidence Bound (UCB1)
- Balances exploration vs exploitation
- Per-source success tracking
- Adaptive source prioritization

#### 1.2 HypothesisGenerator

**File**: `hypothesis.py`

```python
from src.infrastructure.agents.tajine.hunter import HypothesisGenerator, Hypothesis

generator = HypothesisGenerator(llm_client=llm)

hypotheses = await generator.generate(
    context="Analyse du secteur aéronautique en Occitanie",
    territory="31",  # Haute-Garonne
    kg_gaps={"missing": ["supply_chain", "employment"]},
    max_hypotheses=5
)

# Returns List[Hypothesis]
# Hypothesis(statement, confidence, sources_to_check, priority)
```

**Purpose**: Generate search hypotheses from context and knowledge gaps

#### 1.3 GraphExpander

**File**: `graph_expander.py`

```python
from src.infrastructure.agents.tajine.hunter import GraphExpander, KnowledgeGap, GapType

expander = GraphExpander(neo4j_client=neo4j)

# Find gaps in knowledge graph
gaps = await expander.find_gaps(territory="75")

# Returns List[KnowledgeGap]
# KnowledgeGap(type, description, priority, suggested_sources)
# GapType: MISSING_ENTITY, MISSING_RELATION, STALE_DATA, LOW_CONFIDENCE
```

**Purpose**: Identify missing information in Neo4j knowledge graph

#### 1.4 ResilientDataHunter

**File**: `resilient_hunter.py`

```python
from src.infrastructure.agents.tajine.hunter import (
    ResilientDataHunter,
    ResilientHuntResult
)

hunter = ResilientDataHunter(
    sources=["sirene", "bodacc", "boamp"],
    cache_path=Path(".cache/data_hunt"),
    bandit_state_path=Path(".state/bandit.json"),
    retry_attempts=3,
    max_fallbacks=2,
    augment_on_sparse=True,
    sparse_threshold=2
)

result = await hunter.hunt(HuntContext(
    query="entreprises tech département 31",
    territory="31",
    mode="rare",  # normal | question | combler | rare
    max_sources=5
))

# ResilientHuntResult includes:
# - data: List[RawData]
# - cache_hits: int
# - fallbacks_used: int
# - augmentations: int
# - retry_count: int
```

**Features**:
- Retry with exponential backoff
- Per-source circuit breakers
- Automatic fallback chains
- TTL-based caching (24h SIRENE, 1h BODACC/BOAMP)
- Cross-source data augmentation
- Persistent bandit learning

#### 1.5 Fallback Chains

**File**: `resilient.py`

```python
FALLBACK_CHAINS = {
    "sirene": ["insee_api", "data_gouv_sirene", "pappers"],
    "bodacc": ["infogreffe", "pappers", "societe_com"],
    "boamp": ["data_gouv_boamp", "marches_publics"],
    "infogreffe": ["pappers", "societe_com", "bodacc"],
    "ban": ["data_gouv_adresse", "nominatim"],
    "default": ["sirene", "data_gouv"],
}
```

---

## 2. Evaluator

**Location**: `src/infrastructure/agents/tajine/evaluator/`

### Components

#### 2.1 3D Score (Fiabilité × Cohérence × Alpha)

**File**: `scoring.py`

```python
from src.infrastructure.agents.tajine.evaluator import ScoringEngine, Score3D

engine = ScoringEngine()

score = await engine.evaluate(
    data=raw_data,
    context=evaluation_context
)

# Score3D:
# - fiabilite: float (0-1) - Source reliability
# - coherence: float (0-1) - Cross-source consistency
# - alpha: float (0-1) - Novelty/exclusivity
# - combined: float (0-1) - Weighted combination
```

**Dimensions**:
1. **Fiabilité** (Reliability): Source trustworthiness, freshness, official status
2. **Cohérence** (Coherence): Cross-source validation, contradiction detection
3. **Alpha** (Novelty): Information rarity, competitive advantage

#### 2.2 KGValidator

**File**: `kg_validator.py`

```python
from src.infrastructure.agents.tajine.evaluator import KGValidator

validator = KGValidator(neo4j_client=neo4j)

validation = await validator.validate(
    entity={"siren": "123456789", "nom": "ACME Corp"},
    relations=[("LOCATED_IN", "75"), ("SECTOR", "tech")]
)

# Returns:
# - is_valid: bool
# - conflicts: List[Conflict]
# - suggestions: List[Correction]
```

**Purpose**: Validate data against existing knowledge graph

#### 2.3 AlphaTester

**File**: `alpha_tester.py`

```python
from src.infrastructure.agents.tajine.evaluator import AlphaTester

tester = AlphaTester()

alpha_score = await tester.compute_alpha(
    data=new_data,
    existing_corpus=corpus,
    market_context=context
)

# Returns float 0-1 indicating information novelty
```

**Purpose**: Measure information exclusivity and competitive value

---

## 3. CognitiveEngine

**Location**: `src/infrastructure/agents/tajine/cognitive/`

### 5 Cognitive Levels

```
┌─────────────────────────────────────────────────────────────┐
│ Level 5: THEORETICAL - Theory validation + Implementation   │
│ Level 4: STRATEGY - Recommendations + Actions               │
│ Level 3: SCENARIO - Projections + Simulations               │
│ Level 2: CAUSAL - Root cause analysis                        │
│ Level 1: DISCOVERY - Pattern detection + Signals             │
└─────────────────────────────────────────────────────────────┘
```

#### 3.1 Level 1: DiscoveryLevel

**File**: `levels/discovery.py`

```python
from src.infrastructure.agents.tajine.cognitive.levels import DiscoveryLevel

discovery = DiscoveryLevel(llm_provider=llm)

result = await discovery.process(
    results=raw_data_list,
    previous={}
)

# Returns:
# - signals: List[Signal] (growth, decline, opportunity, risk)
# - patterns: List[Pattern]
# - anomalies: List[Anomaly]
# - confidence: float
```

#### 3.2 Level 2: CausalLevel

**File**: `levels/causal.py`

```python
from src.infrastructure.agents.tajine.cognitive.levels import CausalLevel

causal = CausalLevel(llm_provider=llm)

result = await causal.process(
    results=raw_data_list,
    previous={"discovery": discovery_result}
)

# Returns:
# - causes: List[Cause] with confidence scores
# - causal_graph: Dict (relationships)
# - root_causes: List[str]
```

#### 3.3 Level 3: ScenarioLevel

**File**: `levels/scenario.py`

```python
from src.infrastructure.agents.tajine.cognitive.levels import ScenarioLevel

scenario = ScenarioLevel(llm_provider=llm)

result = await scenario.process(
    results=raw_data_list,
    previous={"discovery": ..., "causal": ...}
)

# Returns:
# - optimistic: Scenario
# - baseline: Scenario
# - pessimistic: Scenario
# - key_uncertainties: List[str]
```

#### 3.4 Level 4: StrategyLevel

**File**: `levels/strategy.py`

```python
from src.infrastructure.agents.tajine.cognitive.levels import StrategyLevel

strategy = StrategyLevel(llm_provider=llm)

result = await strategy.process(
    results=raw_data_list,
    previous={"discovery": ..., "causal": ..., "scenario": ...}
)

# Returns:
# - recommendations: List[Recommendation]
# - actions: List[Action]
# - priorities: Dict[str, str]
```

#### 3.5 Level 5: TheoreticalLevel

**File**: `levels/theoretical.py`

```python
from src.infrastructure.agents.tajine.cognitive.levels import TheoreticalLevel

theoretical = TheoreticalLevel(llm_provider=llm)

result = await theoretical.process(
    results=raw_data_list,
    previous={"discovery": ..., "causal": ..., "scenario": ..., "strategy": ...}
)

# Returns:
# - validation: Dict (strongly_supported, supported, neutral, inconsistent)
# - theories_applied: List[Theory]
# - implementation_plans: List[ImplementationPlan]
# - summary: Dict (executive summary)
```

---

## 4. TheoryBank

**Location**: `src/infrastructure/agents/tajine/cognitive/levels/theoretical.py`

### 35 Implemented Theories (6 Categories)

#### Category 1: Regional Growth (6 theories)

| Key | Theory | Author | Indicators |
|-----|--------|--------|------------|
| `growth_pole` | Growth Pole Theory | Perroux (1950) | concentration, growth, spillover |
| `cumulative_causation` | Cumulative Causation | Myrdal (1957) | growth_trend, migration, capital_flow, divergence |
| `unbalanced_growth` | Unbalanced Growth | Hirschman (1958) | forward_linkage, backward_linkage, sector_dominance |
| `core_periphery` | Core-Periphery Model | Friedmann (1966) | dependency, resource_extraction, value_added_location |
| `export_base` | Export Base Theory | North (1955) | export_ratio, multiplier, basic_sector_share |
| `stages_of_growth` | Stages of Economic Growth | Rostow (1960) | development_stage, takeoff_potential, maturity |

#### Category 2: Location (6 theories)

| Key | Theory | Author | Indicators |
|-----|--------|--------|------------|
| `central_place` | Central Place Theory | Christaller (1933) | hierarchy, service_range, threshold |
| `agricultural_location` | Agricultural Location | Von Thünen (1826) | land_rent, distance_to_market, transport_cost |
| `industrial_location` | Industrial Location | Weber (1909) | transport_costs, labor_cost, raw_material_access |
| `bid_rent` | Bid-Rent Theory | Alonso (1964) | land_price, accessibility, density |
| `market_area` | Market Area Theory | Lösch (1940) | market_coverage, competition_distance, demand_density |
| `spatial_competition` | Spatial Competition | Hotelling (1929) | competitor_proximity, market_center, differentiation |

#### Category 3: Agglomeration & NEG (4 theories)

| Key | Theory | Author | Indicators |
|-----|--------|--------|------------|
| `new_economic_geography` | New Economic Geography | Krugman (1991) | agglomeration, transport_costs, scale |
| `industrial_district` | Industrial District | Marshall (1890) | specialization, knowledge_spillover, labor_pool |
| `agglomeration_economies` | Agglomeration Economies | Hoover (1937) | urbanization, localization, firm_density |
| `jacobs_externalities` | Jacobs Externalities | Jacobs (1969) | diversity_index, cross_sector_innovation, urban_density |

#### Category 4: French Territorial Economics (7 theories)

| Key | Theory | Author | Indicators |
|-----|--------|--------|------------|
| `spl` | Systèmes Productifs Localisés | Courlet & Pecqueur (1992) | sme_density, local_supply_chain, tacit_knowledge |
| `milieux_innovateurs` | Milieux Innovateurs | GREMI/Aydalot (1986) | innovation_rate, network_density, institutional_support |
| `economie_proximite` | Économie de Proximité | Rallet & Torre (2004) | geographic_proximity, organized_proximity, coordination_frequency |
| `capital_territorial` | Capital Territorial | Camagni (2008) | infrastructure, social_capital, institutional_quality |
| `ressources_territoriales` | Ressources Territoriales | Colletis & Pecqueur (2005) | latent_resources, activation_potential, collective_action |
| `economie_residentielle` | Économie Résidentielle | Davezies (2008) | residential_income, tourism_share, transfer_income |
| `metropole_archipel` | Économie d'Archipel | Veltz (1996) | metro_connectivity, network_position, inter_metro_flows |

#### Category 5: Innovation & Knowledge (8 theories)

| Key | Theory | Author | Indicators |
|-----|--------|--------|------------|
| `cluster_diamond` | Cluster Diamond | Porter (1990) | factor_conditions, demand_conditions, rivalry, support_industries |
| `endogenous_growth` | Endogenous Growth | Romer/Lucas (1986-88) | rd_intensity, education_level, patent_activity |
| `triple_helix` | Triple Helix Model | Etzkowitz (2000) | university_research, industry_rd, public_support |
| `learning_regions` | Learning Regions | Morgan (1997) | training_rate, adaptation_speed, knowledge_institutions |
| `innovation_systems` | Regional Innovation Systems | Cooke (1992) | innovation_network, institutional_thickness, tech_transfer |
| `knowledge_spillovers` | Knowledge Spillovers | Jaffe (1989) | patent_citations, university_proximity, startup_rate |
| `smart_specialization` | Smart Specialisation | Foray (2009) | specialization_rca, entrepreneurial_discovery, relatedness |
| `creative_class` | Creative Class | Florida (2002) | creative_workers, tolerance_index, amenities |

#### Category 6: Resilience & Sustainability (4 theories)

| Key | Theory | Author | Indicators |
|-----|--------|--------|------------|
| `regional_resilience` | Regional Economic Resilience | Martin (2012) | shock_resistance, recovery_speed, structural_change |
| `evolutionary_econ_geography` | Evolutionary Economic Geography | Boschma (2010) | path_dependence, related_variety, branching |
| `circular_economy` | Circular Economy | Ellen MacArthur (2012) | recycling_rate, industrial_symbiosis, material_efficiency |
| `territorial_ecology` | Écologie Territoriale | Barles (2010) | material_flow, energy_autonomy, ecological_footprint |

### Theory Structure

```python
THEORIES = {
    'theory_key': {
        'name': 'Full Theory Name',
        'author': 'Author (Year)',
        'category': 'category_name',
        'description': 'Brief description of the theory',
        'indicators': ['signal_type_1', 'signal_type_2'],  # Match with Discovery signals
        'strategy_alignment': {
            'investment': 0.85,      # How well theory supports investment
            'monitoring': 0.60,      # How well theory supports monitoring
            'diversification': 0.50, # How well theory supports diversification
            'caution': 0.40,         # How well theory supports caution
            'exit': 0.30             # How well theory supports exit
        }
    }
}
```

---

## 5. AutonomyManager

**Location**: `src/infrastructure/agents/tajine/core/` (integrated in TAJINEAgent)

### Current Implementation (Partial)

```python
class AutonomyLevel(Enum):
    SUPERVISED = 1      # Human approval for all actions
    ASSISTED = 2        # Human approval for significant actions
    COLLABORATIVE = 3   # Parallel work with human oversight
    AUTONOMOUS = 4      # Independent with periodic reports
    FULLY_AUTONOMOUS = 5  # Full independence

# Trust score calculation (simplified)
trust_score = (
    success_rate * 0.4 +
    data_quality * 0.3 +
    user_feedback * 0.3
)
```

### Planned Features (Not Yet Implemented)

- Dedicated AutonomyManager module
- Progressive trust building
- Automatic level adjustment
- Rollback on failures
- Audit logging

---

## Implementation Status

### Completed Components

| Component | Files | Tests | Status |
|-----------|-------|-------|--------|
| SourceBandit | `bandit.py` | 15 | ✅ Complete |
| HypothesisGenerator | `hypothesis.py` | 12 | ✅ Complete |
| GraphExpander | `graph_expander.py` | 18 | ✅ Complete |
| DataHunter | `data_hunter.py` | 10 | ✅ Complete |
| ResilientFetcher | `resilient.py` | 26 | ✅ Complete |
| ResilientDataHunter | `resilient_hunter.py` | 12 | ✅ Complete |
| ScoringEngine (3D) | `scoring.py` | 8 | ✅ Complete |
| KGValidator | `kg_validator.py` | 6 | ✅ Complete |
| AlphaTester | `alpha_tester.py` | 5 | ✅ Complete |
| DiscoveryLevel | `discovery.py` | 4 | ✅ Complete |
| CausalLevel | `causal.py` | 4 | ✅ Complete |
| ScenarioLevel | `scenario.py` | 4 | ✅ Complete |
| StrategyLevel | `strategy.py` | 4 | ✅ Complete |
| TheoreticalLevel | `theoretical.py` | 4 | ✅ Complete |
| TheoryBank | `theoretical.py` | - | ✅ 35/66 theories |

**Total Tests**: 134 passing

### Partial/Missing Components

| Component | Status | Notes |
|-----------|--------|-------|
| AutonomyManager | ⚠️ Partial | Integrated in TAJINEAgent, needs separate module |
| Fine-tuning Pipeline | ❌ Missing | OumiAdapter exists, pipeline not implemented |
| Learning Module | ❌ Missing | RLHF, DPO, GRPO not implemented |
| 31 Additional Theories | ⚠️ Pending | 35/66 theories implemented |

---

## Roadmap

### Phase 1: Complete TheoryBank (Priority: Medium)

Add remaining 31 theories:
- Product Life Cycle (Vernon)
- Input-Output Analysis (Leontief)
- Behavioral Location (Pred)
- Absorptive Capacity (Cohen/Levinthal)
- Open Innovation (Chesbrough)
- Related Variety (Frenken)
- Unrelated Variety (Frenken)
- Etc.

### Phase 2: AutonomyManager Module (Priority: High)

```
src/infrastructure/agents/tajine/autonomy/
├── __init__.py
├── manager.py          # Main AutonomyManager
├── trust_scorer.py     # Trust calculation
├── level_adjuster.py   # Dynamic level adjustment
└── audit.py            # Audit logging
```

### Phase 3: Fine-tuning Pipeline (Priority: High)

```
src/infrastructure/agents/tajine/learning/
├── __init__.py
├── data_generator.py   # Generate training data
├── qlora_trainer.py    # QLoRA fine-tuning
├── dpo_trainer.py      # DPO alignment
├── grpo_trainer.py     # GRPO reasoning
└── territorial_spec.py # Departmental specialization
```

### Phase 4: Integration & Optimization (Priority: Medium)

- Performance optimization
- Monitoring dashboards
- A/B testing framework
- Production deployment

---

## API Quick Reference

### DataHunter

```python
# Basic usage
from src.infrastructure.agents.tajine.hunter import ResilientDataHunter

hunter = ResilientDataHunter(sources=["sirene", "bodacc", "boamp"])
result = await hunter.hunt(HuntContext(query="...", territory="75", mode="normal"))
```

### Evaluator

```python
# Basic usage
from src.infrastructure.agents.tajine.evaluator import ScoringEngine

engine = ScoringEngine()
score = await engine.evaluate(data=raw_data, context=context)
```

### CognitiveEngine

```python
# Basic usage
from src.infrastructure.agents.tajine.cognitive import CognitiveEngine

engine = CognitiveEngine(llm_provider=llm)
analysis = await engine.analyze(data=raw_data, territory="75")
```

### TheoryBank

```python
# Access theories
from src.infrastructure.agents.tajine.cognitive.levels.theoretical import THEORIES

# Get all French territorial theories
french_theories = {k: v for k, v in THEORIES.items() if v.get('category') == 'french_territorial'}

# Get theory by key
growth_pole = THEORIES['growth_pole']
```

---

## References

- [TAJINE Core Algorithm Design](./plans/2025-12-24-tajine-core-algorithm-design.md)
- [TAJINE Cognitive Engine Design](./plans/2025-12-13-tajine-cognitive-engine-design.md)
- [TAJINE Agentic Architecture](./plans/2025-12-14-tajine-agentic-architecture-design.md)
- [TAJINE User Guide](./TAJINE-Guide-Utilisateur.md)
