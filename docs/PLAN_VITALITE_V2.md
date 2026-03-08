# 🎯 Plan Vitalité Territoriale V2

*Généré le 5 février 2026*

---

## Vision

Transformer l'indice de vitalité en **outil prédictif** capable de :
- Anticiper les crises économiques locales
- Identifier les opportunités de développement
- Fournir des alertes automatiques aux décideurs

---

## Phase 1 : Fondations Data (Semaine 1)

### 1.1 Historisation des métriques
**Objectif** : Stocker les données quotidiennement pour analyser les tendances

| Tâche | Effort | Priorité |
|-------|--------|----------|
| Créer table `territorial_metrics_history` | 2h | 🔴 Haute |
| Cron job collecte quotidienne (tous les depts) | 3h | 🔴 Haute |
| API endpoint `/territorial/history/{code}` | 2h | 🔴 Haute |
| Backfill 30 jours si données dispo | 4h | 🟡 Moyenne |

**Schema proposé** :
```sql
CREATE TABLE territorial_metrics_history (
    id SERIAL PRIMARY KEY,
    territory_code VARCHAR(5),
    collected_at TIMESTAMP,
    -- Métriques brutes
    creations INT,
    closures INT,
    procedures INT,
    job_offers INT,
    unemployment_rate DECIMAL(4,2),
    real_estate_tx INT,
    avg_price_sqm DECIMAL(10,2),
    -- Calculés
    vitality_index DECIMAL(5,2),
    net_creation INT,
    -- Metadata
    sources_used JSONB
);
```

### 1.2 Enrichissement sectoriel (NAF)
**Objectif** : Comprendre QUELS secteurs bougent

| Tâche | Effort | Priorité |
|-------|--------|----------|
| Parser code NAF depuis BODACC | 2h | 🔴 Haute |
| Grouper par secteur (17 sections NAF) | 2h | 🔴 Haute |
| Top 5 secteurs créateurs / destructeurs | 2h | 🟡 Moyenne |
| Widget frontend "Secteurs" | 3h | 🟡 Moyenne |

**Sections NAF principales** :
- A: Agriculture
- C: Industrie manufacturière
- F: Construction
- G: Commerce
- I: Hébergement/restauration
- J: Information/communication
- M: Activités scientifiques
- N: Services administratifs

---

## Phase 2 : Signaux Prédictifs (Semaine 2)

### 2.1 Indicateurs avancés
**Objectif** : Détecter les problèmes AVANT qu'ils n'arrivent

| Signal | Formule | Seuil alerte |
|--------|---------|--------------|
| **Stress entreprises** | modifications / créations | > 3.0 |
| **Hémorragie** | fermetures / créations | > 1.5 |
| **Tension emploi** | offres / demandeurs | < 0.3 |
| **Bulle immo** | variation prix M-3 | > +15% |
| **Désertification** | radiations commerces (NAF G) | > 2x moyenne |

| Tâche | Effort | Priorité |
|-------|--------|----------|
| Implémenter SignalDetector v2 | 4h | 🔴 Haute |
| Calcul des 5 indicateurs avancés | 3h | 🔴 Haute |
| Système de scoring des alertes | 2h | 🔴 Haute |
| Tests unitaires signaux | 2h | 🟡 Moyenne |

### 2.2 Tendances temporelles
**Objectif** : Comparer avec le passé

| Métrique | Calcul |
|----------|--------|
| Variation M-1 | (actuel - mois_precedent) / mois_precedent |
| Variation T-1 | vs même mois année précédente |
| Moyenne mobile 3 mois | lissage des variations |
| Accélération | variation de la variation |

| Tâche | Effort | Priorité |
|-------|--------|----------|
| Endpoint `/territorial/trends/{code}` | 3h | 🔴 Haute |
| Calcul variations M-1, M-3, A-1 | 2h | 🔴 Haute |
| Graphique tendances frontend | 4h | 🟡 Moyenne |

---

## Phase 3 : Score Décomposé (Semaine 3)

### 3.1 Contribution par source
**Objectif** : Expliquer POURQUOI un territoire a ce score

```
Vitalité: 65.0
├── Entreprises (BODACC):  +12 pts  ████████████
├── Emploi (France Travail): +8 pts  ████████
├── Chômage (INSEE):        -5 pts  █████ (négatif)
├── Immobilier (DVF):       +3 pts  ███
└── Base:                   50 pts
```

| Tâche | Effort | Priorité |
|-------|--------|----------|
| Refactorer vitality_index avec breakdown | 3h | 🔴 Haute |
| API retourne `vitality_breakdown` | 2h | 🔴 Haute |
| Widget frontend "Décomposition" | 4h | 🟡 Moyenne |
| Tooltip explicatif par composante | 2h | 🟢 Basse |

### 3.2 Benchmarking
**Objectif** : Comparer à des références

| Référence | Usage |
|-----------|-------|
| Moyenne nationale | "Ce dept est 15% au-dessus de la moyenne" |
| Moyenne régionale | Comparaison locale |
| Départements similaires | Par population/densité |
| Historique du dept | "En hausse de 5 pts vs 2025" |

| Tâche | Effort | Priorité |
|-------|--------|----------|
| Calcul moyennes nationales/régionales | 3h | 🟡 Moyenne |
| Percentile ranking (top 10%, etc.) | 2h | 🟡 Moyenne |
| Badge "Champion régional" / "En difficulté" | 2h | 🟢 Basse |

---

## Phase 4 : Alertes & Automatisation (Semaine 4)

### 4.1 Système d'alertes
**Objectif** : Notifier automatiquement les anomalies

| Type alerte | Condition | Canal |
|-------------|-----------|-------|
| 🔴 Critique | Vitalité chute > 15 pts / mois | Email + SMS |
| 🟠 Warning | Procédures +50% vs M-1 | Email |
| 🟡 Info | Nouveau dans top 10 | Dashboard |
| 🟢 Positif | Remontée > 10 pts | Dashboard |

| Tâche | Effort | Priorité |
|-------|--------|----------|
| Table `territorial_alerts` | 1h | 🟡 Moyenne |
| Job détection anomalies quotidien | 3h | 🟡 Moyenne |
| Endpoint `/alerts` | 2h | 🟡 Moyenne |
| Intégration notifications (email/webhook) | 4h | 🟢 Basse |

### 4.2 Rapports automatiques
**Objectif** : Générer des synthèses périodiques

| Rapport | Fréquence | Contenu |
|---------|-----------|---------|
| Flash quotidien | Chaque jour | Top 5 mouvements |
| Hebdo régional | Lundi | Synthèse par région |
| Mensuel national | 1er du mois | Analyse complète France |

| Tâche | Effort | Priorité |
|-------|--------|----------|
| Template rapport Markdown/PDF | 3h | 🟢 Basse |
| Génération automatique via cron | 2h | 🟢 Basse |
| Envoi par email | 2h | 🟢 Basse |

---

## Phase 5 : Intelligence TAJINE (Semaine 5+)

### 5.1 Analyse narrative
**Objectif** : TAJINE explique les chiffres en langage naturel

```
"Le Rhône connaît un ralentissement modéré ce mois-ci (-2 pts).
La cause principale est la hausse des fermetures dans le commerce
de détail (+40%), probablement liée aux travaux du centre-ville.
Cependant, le secteur tech reste dynamique avec 15 créations.
Recommandation : surveiller le commerce, opportunité dans la tech."
```

| Tâche | Effort | Priorité |
|-------|--------|----------|
| Prompt engineering analyse territoriale | 4h | 🟡 Moyenne |
| Intégration TAJINE → métriques | 3h | 🟡 Moyenne |
| Cache analyses (éviter re-génération) | 2h | 🟢 Basse |

### 5.2 Prédictions ML (optionnel)
**Objectif** : Prédire la vitalité à 3 mois

| Approche | Complexité | Données requises |
|----------|------------|------------------|
| Régression linéaire | Faible | 6 mois historique |
| ARIMA | Moyenne | 12 mois historique |
| Prophet (Facebook) | Moyenne | 12 mois + saisonnalité |
| LSTM | Haute | 24 mois + features |

*À évaluer après 3 mois de collecte de données.*

---

## Résumé des efforts

| Phase | Durée estimée | Priorité |
|-------|---------------|----------|
| Phase 1 : Fondations Data | 1 semaine | 🔴 Critique |
| Phase 2 : Signaux Prédictifs | 1 semaine | 🔴 Haute |
| Phase 3 : Score Décomposé | 1 semaine | 🟡 Moyenne |
| Phase 4 : Alertes | 1 semaine | 🟡 Moyenne |
| Phase 5 : TAJINE Intelligence | 2+ semaines | 🟢 Nice-to-have |

**Total estimé : 5-6 semaines** pour un MVP complet.

---

## Quick Wins (< 1 jour chacun)

1. ✅ ~~Intégrer France Travail~~ (fait)
2. ✅ ~~Intégrer INSEE chômage~~ (fait)
3. ✅ ~~Intégrer DVF~~ (fait)
4. ⬜ Ajouter le breakdown dans l'API
5. ⬜ Parser les codes NAF depuis BODACC
6. ⬜ Créer la table d'historique

---

## Prochaine action recommandée

**→ Phase 1.1 : Historisation des métriques**

Sans historique, impossible de calculer des tendances ou de détecter des anomalies. C'est la fondation de tout le reste.

Commencer par :
1. Créer la table PostgreSQL
2. Cron job de collecte quotidienne
3. Backfill 30 jours si possible

Tu valides ce plan ? 🦞
