# TAJINE - APIs Disponibles et Capacités Agent

**Date:** 2025-12-28
**Complément de:** DIAGNOSTIC.md

---

## 1. APIs Gratuites Recommandées

### 1.1 APIs Déjà Intégrées

| API | Statut | Description | Limite |
|-----|--------|-------------|--------|
| [SIRENE](https://api.gouv.fr/les-api/sirene_v3) | ✅ Actif | Données entreprises (SIRET, NAF) | Illimité |
| [BODACC](https://bodacc-datadila.opendatasoft.com) | ✅ Actif | Créations/radiations/procédures | Illimité |
| [BOAMP](https://boamp-datadila.opendatasoft.com) | ✅ Actif | Marchés publics | Illimité |
| [BAN](https://api-adresse.data.gouv.fr) | ✅ Actif | Géocodage adresses France | Illimité |
| [Subventions](https://aides-territoires.beta.gouv.fr) | ✅ Actif | Aides aux entreprises | Illimité |

### 1.2 APIs à Intégrer (Haute Priorité)

| API | URL | Description | Valeur TAJINE |
|-----|-----|-------------|---------------|
| **INSEE Données Locales** | [api.insee.fr](https://api.insee.fr/catalogue/) | Statistiques territoriales, revenus, emploi | Agrégation par commune/département |
| **DVF (Valeurs Foncières)** | [app.dvf.etalab.gouv.fr](https://app.dvf.etalab.gouv.fr/) | Prix immobilier par parcelle | Analyse marché immobilier territorial |
| **Open Urssaf** | [open.urssaf.fr](https://api.gouv.fr/les-api/api-open-data-urssaf) | Effectifs salariés, cotisations | Dynamique emploi par secteur/zone |
| **France Travail** | [francetravail.io](https://francetravail.io/data/api/offres-emploi) | 500k offres d'emploi/jour | Tension marché travail territorial |
| **API Carto Cadastre** | [apicarto.ign.fr](https://apicarto.ign.fr/api/doc/cadastre) | Parcelles, zonage | Analyse foncière |

### 1.3 APIs à Intégrer (Moyenne Priorité)

| API | URL | Description | Valeur TAJINE |
|-----|-----|-------------|---------------|
| **INPI/RNE** | [data.inpi.fr](https://data.inpi.fr/content/editorial/Acces_API_Entreprises) | Registre National Entreprises + comptes | Bilans financiers, dirigeants |
| **Les-Aides.fr** | [les-aides.fr/api](https://les-aides.fr/api) | Catalogue aides CCI | Subventions par territoire |
| **Légifrance** | [api.gouv.fr](https://api.gouv.fr/les-api/api_legifrance) | Textes juridiques | Veille réglementaire |
| **OpenStreetMap Nominatim** | [nominatim.org](https://nominatim.org/) | Géocodage mondial | Backup BAN + POI |

### 1.4 APIs Régionales Open Data

| Région | Portail | Données Clés |
|--------|---------|--------------|
| Île-de-France | [data.iledefrance.fr](https://data.iledefrance.fr) | Transports, économie, environnement |
| Nouvelle-Aquitaine | [data.nouvelle-aquitaine.fr](https://data.nouvelle-aquitaine.fr) | Agriculture, tourisme |
| Auvergne-Rhône-Alpes | [data.auvergnerhonealpes.fr](https://data.auvergnerhonealpes.fr) | Industrie, innovation |

---

## 2. Capacités de l'Agent TAJINE

### 2.1 Architecture Cognitive

```
┌─────────────────────────────────────────────────────────────┐
│                    Requête Complexe                          │
│  "Analyse comparative France 2030 pour le 75 et 69"         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ PERCEIVE: Extraction d'intent                                │
│ → intent: "analyze", territory: ["75", "69"], sector: null   │
│ → raw_query stocké pour browser_action                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ PLAN: Décomposition LLM (ou règles)                          │
│ → Subtask 1: browser_action (France 2030 web search)         │
│ → Subtask 2: territorial_data (SIRENE 75)                    │
│ → Subtask 3: territorial_data (SIRENE 69)                    │
│ → Subtask 4: analyze_data (comparaison)                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ DELEGATE: Exécution via ManusAgent ou ToolRegistry           │
│ → browser_action: Screenshot + extraction web                │
│ → territorial_data: Requêtes SIRENE parallèles               │
│ → analyze_data: Agrégation statistique                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ SYNTHESIZE: Fusion 5 niveaux cognitifs                       │
│                                                              │
│ Level 1 - Discovery: Patterns détectés (signaux faibles)    │
│ Level 2 - Causal: Relations cause-effet (DAG)               │
│ Level 3 - Scenario: Projections Monte Carlo                 │
│ Level 4 - Strategy: Recommandations prioritisées            │
│ Level 5 - Theoretical: Validation théories économiques      │
│                                                              │
│ → UnifiedSynthesis avec Markdown formaté                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ LEARN: Mise à jour confiance + collecte training             │
│ → TrustManager: tool_trust[browser_action] += success        │
│ → DataCollector: Interaction enregistrée pour fine-tuning    │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Niveaux de Complexité Supportés

| Niveau | Exemple Requête | Traitement | Modèle LLM |
|--------|-----------------|------------|------------|
| **Simple** | "Combien d'entreprises tech à Paris?" | PPDSL rapide, 1-2 outils | LOCAL (qwen3:14b) |
| **Modéré** | "Tendances créations commerce Rhône 2024" | PPDSL complet, 3-4 outils | STANDARD |
| **Complexe** | "Analyse comparative France 2030 sur 5 départements" | PPDSL + 5 niveaux cognitifs | POWERFUL (32b) |
| **Critique** | "Modèle prédictif radiations industrie Hauts-de-France" | PPDSL + Monte Carlo + Theoretical | MAXIMUM (72b) |

### 2.3 Forces Actuelles

| Capacité | Score | Détails |
|----------|-------|---------|
| **Décomposition de tâches** | ⭐⭐⭐⭐ | LLM + règles avec fallback robuste |
| **Multi-source data** | ⭐⭐⭐⭐ | 5+ APIs intégrées, cache Redis |
| **Analyse territoriale** | ⭐⭐⭐⭐ | Agrégation par département/région |
| **Navigation web** | ⭐⭐⭐ | Playwright avec Agent Live streaming |
| **Raisonnement causal** | ⭐⭐⭐ | DAG + corrélations, pas d'inférence causale profonde |
| **Projections** | ⭐⭐⭐ | Monte Carlo basique implémenté |
| **Recommandations** | ⭐⭐⭐⭐ | Prioritisation claire, format structuré |

### 2.4 Faiblesses Identifiées

| Limitation | Impact | Solution Proposée |
|------------|--------|-------------------|
| **Mode Complet = Rapide** | UX trompeuse | Router vers modèle 32b+ en mode "complete" |
| **Pas de mémoire inter-session** | Contexte perdu | Implémenter pgvector pour mémoire épisodique |
| **Theoretical level partiel** | Analyse incomplète | Enrichir `theories.json` avec 66 théories économiques |
| **Trust ratio négatif** | Autonomie bloquée | Auditer les 27 échecs, améliorer prompts outils |
| **Training data vide** | Pas d'amélioration | Déboguer callbacks DataCollector |
| **Pas de feedback loop** | Corrections perdues | Endpoint `/api/v1/tajine/feedback` |

### 2.5 Capacités Requêtes Complexes

**L'agent PEUT gérer:**

1. **Analyses multi-territoriales**
   - Comparaison jusqu'à 10 départements simultanés
   - Agrégation par région automatique
   - Visualisation différentielle

2. **Analyses temporelles**
   - Historique BODACC sur 5 ans
   - Tendances mensuelles/trimestrielles
   - Détection de saisonnalité

3. **Analyses sectorielles**
   - Codes NAF complets
   - Hiérarchie secteur/sous-secteur
   - Comparaison inter-secteurs

4. **Web research**
   - Recherche DuckDuckGo via browser_action
   - Extraction contenu pages web
   - Screenshots pour Agent Live

**L'agent NE PEUT PAS (encore):**

1. **Inférence causale profonde**
   - Pas de DoWhy/CausalML intégré
   - Corrélations ≠ causalité

2. **Prédictions ML avancées**
   - Pas de modèles entraînés
   - Monte Carlo basique seulement

3. **Graphe de connaissances**
   - Pas de Neo4j intégré
   - Relations entités non persistées

4. **Analyse de sentiments**
   - Pas d'analyse NLP des actualités
   - Pas de score de réputation

---

## 3. Comparaison avec État de l'Art

### 3.1 vs Agents Commerciaux

| Critère | TAJINE | AgentGPT | AutoGPT | LangChain Agents |
|---------|--------|----------|---------|------------------|
| Multi-tool orchestration | ✅ PPDSL | ✅ | ✅ | ✅ |
| Mémoire persistante | ⚠️ Partiel | ✅ | ✅ | ✅ |
| Fine-tuning auto | ⚠️ Non actif | ❌ | ❌ | ❌ |
| 5 niveaux cognitifs | ✅ Unique | ❌ | ❌ | ❌ |
| Trust management | ✅ Unique | ❌ | ❌ | ❌ |
| Domain-specific (FR) | ✅ Spécialisé | ❌ Générique | ❌ | ❌ |

### 3.2 Points Différenciants TAJINE

1. **Cycle PPDSL** - Architecture unique avec 5 phases distinctes
2. **5 Niveaux Cognitifs** - Progression discovery→theoretical
3. **Trust Management** - Confiance par outil avec seuils d'autonomie
4. **Spécialisation territoriale** - APIs françaises natives
5. **Fine-tuning pipeline** - SFT/DPO automatique (à activer)

---

## 4. Recommandations d'Amélioration

### 4.1 Court Terme (Semaines 1-2)

```python
# 1. Différencier mode Rapide/Complet dans llm_router.py
if mode == "complete":
    return ModelTier.POWERFUL  # 32b au lieu de 14b

# 2. Activer DataCollector callbacks dans tajine_agent.py
await self.data_collector.record_success(interaction)
```

### 4.2 Moyen Terme (Semaines 3-6)

1. **Intégrer INSEE Données Locales**
   - Revenus moyens par commune
   - Taux de chômage par zone d'emploi
   - Démographie entreprises

2. **Intégrer DVF**
   - Prix immobilier par territoire
   - Tendances marché foncier

3. **Intégrer France Travail**
   - Offres d'emploi par secteur/territoire
   - Tension marché du travail

### 4.3 Long Terme (Mois 2-3)

1. **Mémoire épisodique pgvector**
2. **Graphe de connaissances Neo4j**
3. **Inférence causale DoWhy**
4. **Dashboard monitoring Langfuse**

---

## 5. Sources

- [api.gouv.fr](https://api.gouv.fr/) - Catalogue APIs du service public
- [data.gouv.fr](https://www.data.gouv.fr/dataservices) - Portail open data national
- [INSEE API Catalogue](https://api.insee.fr/catalogue/) - APIs statistiques INSEE
- [DVF Etalab](https://app.dvf.etalab.gouv.fr/) - Valeurs foncières
- [Open Urssaf](https://open.urssaf.fr) - Données sociales
- [France Travail IO](https://francetravail.io) - APIs emploi
- [API Carto IGN](https://apicarto.ign.fr/) - Données cadastrales
- [Nominatim OSM](https://nominatim.org/) - Géocodage OpenStreetMap

---

*Document généré par Claude Code (Opus 4.5)*
