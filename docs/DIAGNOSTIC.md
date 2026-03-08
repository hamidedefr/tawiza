# TAJINE - Diagnostic Technique Complet

**Date:** 2025-12-28
**Version:** MPtoO-V2
**Auditeur:** Claude Code (Opus 4.5)

---

## 1. Vue d'Ensemble

TAJINE (Territorial Analysis Joint Intelligence Network Engine) est un agent agentique d'intelligence territoriale française. Il utilise le cycle PPDSL avec 5 niveaux cognitifs pour analyser les données économiques territoriales.

### 1.1 État Global

| Composant | État | Score |
|-----------|------|-------|
| Backend API | ✅ Opérationnel | 85% |
| Frontend Next.js | ⚠️ Partiel | 60% |
| Agent TAJINE | ✅ Fonctionnel | 80% |
| Système de mémoire | ⚠️ Basique | 50% |
| APIs externes | ✅ Actives | 90% |

---

## 2. APIs et Sources de Données

### 2.1 APIs Actives (Gratuites, Sans Clé)

| API | Endpoint | Statut | Usage |
|-----|----------|--------|-------|
| **SIRENE** | `recherche-entreprises.api.gouv.fr` | ✅ Active | Recherche entreprises (SIRET, NAF, dept) |
| **BODACC** | `bodacc-datadila.opendatasoft.com` | ✅ Active | Créations, radiations, procédures |
| **BOAMP** | `boamp-datadila.opendatasoft.com` | ✅ Active | Marchés publics |
| **BAN** | `api-adresse.data.gouv.fr` | ✅ Active | Géocodage adresses |
| **Subventions** | `aides-territoires.beta.gouv.fr` | ✅ Active | Aides et subventions |

### 2.2 Services Configurés

| Service | Configuration | Statut |
|---------|---------------|--------|
| **PostgreSQL** | `localhost:5432/mptoo` | ✅ Connecté |
| **Redis** | `localhost:6379` | ✅ Connecté |
| **Ollama** | `localhost:11434` | ✅ Actif (qwen2.5:14b) |
| **Label Studio** | `localhost:8080` | ⚠️ Non vérifié |
| **Langfuse** | Configuré | ⚠️ Non vérifié |
| **MinIO** | Configuré | ⚠️ Non vérifié |

### 2.3 APIs Manquantes ou Inactives

| API | Clé Requise | Priorité | Impact |
|-----|-------------|----------|--------|
| **Sentry** | DSN vide | Moyenne | Pas de monitoring erreurs |
| **Skyvern** | Clé vide | Basse | Browser automation limitée |
| **INSEE Direct** | Non configuré | Haute | Données statistiques officielles |
| **OpenData Soft Premium** | Non configuré | Moyenne | Limites de requêtes |

---

## 3. Algorithme TAJINE

### 3.1 Cycle PPDSL

```
┌─────────────┐
│   PERCEIVE  │ ← Collecte données (SIRENE, BODACC, etc.)
└──────┬──────┘
       ▼
┌─────────────┐
│    PLAN     │ ← Stratégie d'analyse (LLM routing)
└──────┬──────┘
       ▼
┌─────────────┐
│  DELEGATE   │ ← Exécution outils (ToolRegistry)
└──────┬──────┘
       ▼
┌─────────────┐
│ SYNTHESIZE  │ ← Fusion multi-niveaux (UnifiedSynthesizer)
└──────┬──────┘
       ▼
┌─────────────┐
│   LEARN     │ ← Mise à jour trust + collecte training
└─────────────┘
```

**État:** ✅ Implémenté dans `tajine_agent.py`

### 3.2 Niveaux Cognitifs

| Niveau | Description | Implémentation |
|--------|-------------|----------------|
| **Discovery** | Exploration initiale | ✅ Actif |
| **Causal** | Relations cause-effet | ✅ Actif |
| **Scenario** | Projections futures | ✅ Actif |
| **Strategy** | Recommandations | ✅ Actif |
| **Theoretical** | Modèles abstraits | ⚠️ Partiel |

### 3.3 Routing LLM (HybridLLMRouter)

| Tier | Modèle | Cas d'usage |
|------|--------|-------------|
| LOCAL | `qwen2.5:3b` | Tâches simples |
| STANDARD | `qwen2.5:14b` | Analyses courantes |
| POWERFUL | `qwen2.5:32b` | Analyses complexes |
| MAXIMUM | `qwen2.5:72b` | Raisonnement avancé |

**Problème identifié:** Mode "Complet" n'utilise pas réellement un modèle plus puissant (même comportement que "Rapide").

---

## 4. Agent Agentique

### 4.1 Capacités Actuelles

| Capacité | État | Détails |
|----------|------|---------|
| **Recherche entreprises** | ✅ | Via SIRENE API |
| **Analyse territoriale** | ✅ | Agrégation par département |
| **Détection patterns** | ⚠️ | Basique, pas de ML |
| **Navigation web** | ⚠️ | Playwright limité |
| **Génération rapports** | ✅ | Markdown + JSON |

### 4.2 Trust Manager

État actuel du fichier `data/tajine/trust.json`:

```json
{
  "trust_score": 0.60,
  "autonomy_level": "SEMI_AUTONOMOUS",
  "success_count": 16,
  "failure_count": 27,
  "tool_trust": {
    "analyze_data": {"trust_score": 1.0, "success_count": 29},
    "territorial_data": {"trust_score": 1.0, "success_count": 36},
    "browser_action": {"trust_score": 0.75, "success_count": 15, "failure_count": 4}
  }
}
```

**Observations:**
- Trust global à 60% (seuil SEMI_AUTONOMOUS)
- 27 échecs vs 16 succès → ratio problématique
- `browser_action` avec 4 échecs (navigation web)

### 4.3 Outils Disponibles (ToolRegistry)

| Catégorie | Outils | État |
|-----------|--------|------|
| **Data** | sirene_query, bodacc_search, boamp_search | ✅ |
| **Geo** | geocode, territorial_data | ✅ |
| **Browser** | browser_action, screenshot | ⚠️ |
| **Analysis** | analyze_data, monte_carlo | ✅ |

---

## 5. Système de Mémoire et Apprentissage

### 5.1 Composants Mémoire

| Type | Stockage | État |
|------|----------|------|
| **Trust scores** | JSON (`data/tajine/trust.json`) | ✅ Actif |
| **Training data** | JSON (`data/tajine/training_data.json`) | ⚠️ Vide |
| **Conversations** | PostgreSQL | ✅ Actif |
| **Cache requêtes** | Redis | ✅ Actif |

### 5.2 DataCollector (Fine-tuning)

```python
# Seuils de déclenchement
min_examples_trigger = 100  # Pour SFT
min_preferences_trigger = 50  # Pour DPO
```

**État actuel:**
- 0 exemples SFT collectés
- 0 paires DPO collectées
- Fine-tuning non déclenché

### 5.3 Manques Identifiés

1. **Pas de mémoire épisodique** - L'agent ne retient pas le contexte des sessions précédentes
2. **Pas de graphe de connaissances** - Relations entre entités non persistées
3. **Pas de feedback loop** - Les corrections utilisateur ne sont pas apprises
4. **Training data vide** - Aucune donnée collectée malgré le système en place

---

## 6. Frontend

### 6.1 Pages et État

| Page | Route | État | Problèmes |
|------|-------|------|-----------|
| **AI Chat** | `/dashboard/ai-chat` | ⚠️ | Mode Complet = Rapide |
| **TAJINE** | `/dashboard/tajine` | ⚠️ | Données MOCK |
| **Analytics** | `/dashboard/analytics` | ⚠️ | Pas de refresh WebSocket |
| **Agent Live** | `/dashboard/agent-live` | ❌ | VNC non fonctionnel |

### 6.2 Problèmes UI Identifiés

#### Onglet Chat TAJINE
- [ ] Mode "Complet" identique à "Rapide" (même modèle LLM)
- [ ] Pas d'affichage du niveau cognitif atteint
- [ ] Pas de visualisation du cycle PPDSL en cours

#### Onglet Carte France
- [ ] Données MOCK (pas de vraies stats départementales)
- [ ] KPI Panel sans données réelles
- [ ] Pas de layer satellite/réaliste

#### Onglet Analytics
- [ ] Graphiques avec données fictives
- [ ] Pas de synchronisation temps réel
- [ ] Historique conversations non lié

#### Onglet Départements
- [ ] Liste statique
- [ ] Pas de drill-down vers détails

### 6.3 Composants Charts

| Chart | Fichier | Données |
|-------|---------|---------|
| FranceMap | `FranceMap.tsx` | ⚠️ MOCK |
| GrowthLineChart | `GrowthLineChart.tsx` | ⚠️ MOCK |
| HeatmapChart | `HeatmapChart.tsx` | ⚠️ MOCK |
| RadarChart | `RadarChart.tsx` | ⚠️ MOCK |
| SankeyChart | `SankeyChart.tsx` | ⚠️ MOCK |
| TreemapChart | `TreemapChart.tsx` | ⚠️ MOCK |
| MonteCarloChart | `MonteCarloChart.tsx` | ⚠️ MOCK |
| RelationGraph | `RelationGraph.tsx` | ⚠️ MOCK |

---

## 7. Problèmes Critiques

### 7.1 Priorité Haute

1. **Mode Complet non différencié**
   - Impact: UX trompeuse, attentes non satisfaites
   - Fix: Router vers modèle 32b/72b en mode Complet

2. **Données MOCK partout**
   - Impact: Dashboard inutilisable en production
   - Fix: Connecter aux vraies APIs + agréger

3. **Training data jamais collecté**
   - Impact: Pas d'amélioration continue
   - Fix: Déboguer DataCollector, vérifier callbacks

### 7.2 Priorité Moyenne

4. **Trust ratio négatif (27 échecs / 16 succès)**
   - Impact: Autonomie bloquée à SEMI_AUTONOMOUS
   - Fix: Auditer les échecs, améliorer prompts outils

5. **WebSocket non synchronisé**
   - Impact: Pas de temps réel entre onglets
   - Fix: Implémenter TAJINEHandler broadcast

6. **Niveau Theoretical partiel**
   - Impact: Analyse incomplète
   - Fix: Compléter theories.json + scorer

### 7.3 Priorité Basse

7. **Agent Live VNC non fonctionnel**
   - Impact: Pas de visualisation browser
   - Fix: Reconfigurer container Selenium/browserless

8. **APIs monitoring absentes**
   - Impact: Pas de visibilité production
   - Fix: Configurer Sentry DSN

---

## 8. Métriques de Performance

### 8.1 Backend

| Métrique | Valeur | Cible |
|----------|--------|-------|
| Temps réponse moyen | ~3-5s | <2s |
| Taux succès outils | 37% | >80% |
| Cache hit ratio | N/A | >60% |

### 8.2 Frontend

| Métrique | Valeur | Cible |
|----------|--------|-------|
| First Contentful Paint | ~2s | <1s |
| Time to Interactive | ~4s | <2s |
| Bundle size | ~800KB | <500KB |

---

## 9. Recommandations Immédiates

### Court terme (1-2 semaines)

1. **Corriger le routing LLM** pour différencier Rapide/Complet
2. **Connecter les charts** aux vraies APIs SIRENE/BODACC
3. **Déboguer DataCollector** pour activer la collecte

### Moyen terme (1 mois)

4. **Implémenter endpoint `/api/tajine/department-stats`**
5. **Ajouter WebSocket broadcast** pour synchronisation
6. **Auditer et corriger les 27 échecs** du trust manager

### Long terme (3 mois)

7. **Ajouter mémoire épisodique** (Neo4j ou pgvector)
8. **Implémenter feedback loop** utilisateur → training
9. **Dashboard monitoring** avec Grafana/Langfuse

---

## 10. Annexes

### A. Fichiers Clés

```
src/infrastructure/agents/tajine/
├── tajine_agent.py          # Agent principal + PPDSL
├── llm_router.py             # HybridLLMRouter
├── planning.py               # PlanningEngine
├── cognitive/
│   ├── synthesizer.py        # UnifiedSynthesizer
│   └── levels/               # 5 niveaux cognitifs
├── learning/
│   ├── data_collector.py     # Collecte training data
│   └── trust_manager.py      # Gestion confiance
└── tools/                    # Outils disponibles
```

### B. Variables d'Environnement Requises

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
REDIS_URL=redis://localhost:6379/0
OLLAMA_URL=http://localhost:11434
SENTRY_DSN=<à configurer>
```

### C. Endpoints API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/tajine/analyze` | Lancer analyse TAJINE |
| GET | `/api/v1/tajine/status` | État agent |
| WS | `/ws` | WebSocket temps réel |
| GET | `/api/v1/analytics` | Métriques globales |

---

*Document généré automatiquement par Claude Code (Opus 4.5)*
