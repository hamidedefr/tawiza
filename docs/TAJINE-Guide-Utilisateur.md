# TAJINE - Guide Utilisateur

## Qu'est-ce que TAJINE ?

**TAJINE** (Territorial Analysis & Joint Intelligence for Networked Environments) est un assistant intelligent qui aide à comprendre et anticiper l'évolution des territoires et des entreprises en France.

### La Métaphore du Tajine

Comme le plat marocain traditionnel qui mélange lentement différents ingrédients pour créer une saveur unique, TAJINE combine des informations de sources variées (économiques, sociales, géographiques) pour produire une vision claire et des prédictions sur l'avenir d'un territoire.

---

## Pourquoi TAJINE ?

### Le Problème

Les décideurs (collectivités, services de l'État, entreprises) font face à un défi :

- **Trop d'informations** dispersées dans des dizaines de sources différentes
- **Pas assez de temps** pour tout analyser manuellement
- **Difficulté à anticiper** les crises avant qu'elles n'arrivent
- **Risque de passer à côté** d'opportunités ou de signaux d'alerte

### La Solution TAJINE

TAJINE agit comme un **analyste expert infatigable** qui :

1. **Collecte** automatiquement les données de sources officielles et publiques
2. **Analyse** ces données pour détecter des tendances et des signaux
3. **Anticipe** les évolutions futures (risques, opportunités)
4. **Recommande** des actions concrètes

---

## Pour Qui ?

### Collectivités Territoriales

- Suivre la santé économique de leur territoire
- Anticiper les fermetures d'entreprises
- Identifier les secteurs en croissance
- Évaluer l'attractivité de leurs zones d'activité

### Services de l'État (Préfectures, DREETS)

- Produire des notes de conjoncture économique
- Surveiller les filières industrielles stratégiques
- Détecter les risques sociaux (plans sociaux à venir)
- Coordonner l'action publique

### Acteurs Économiques

- Prospecter de nouveaux clients ou partenaires
- Évaluer des fournisseurs ou concurrents
- Identifier des opportunités d'implantation

---

## Comment ça Marche ?

### Le Cycle PPDSL (en termes simples)

TAJINE suit un processus en 5 étapes, comme un analyste humain le ferait :

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  PERCEVOIR  │───▶│  PLANIFIER  │───▶│  DÉLÉGUER   │
│             │    │             │    │             │
│ Comprendre  │    │ Où chercher │    │ Collecter   │
│ la question │    │ l'info ?    │    │ les données │
└─────────────┘    └─────────────┘    └─────────────┘
                                             │
                                             ▼
               ┌─────────────┐    ┌─────────────┐
               │  APPRENDRE  │◀───│ SYNTHÉTISER │
               │             │    │             │
               │ S'améliorer │    │ Analyser et │
               │ avec le     │    │ répondre    │
               │ feedback    │    │             │
               └─────────────┘    └─────────────┘
```

### Exemple Concret

**Vous demandez :** "Quelles PME industrielles sont à risque dans l'Hérault ?"

**TAJINE fait :**

1. **Percevoir** : Comprend que vous cherchez des entreprises de 10-250 salariés, dans l'industrie, département 34, avec un risque de difficulté

2. **Planifier** : Décide de consulter :
   - SIRENE (registre des entreprises)
   - BODACC (annonces légales de faillites)
   - La presse locale (signaux faibles)

3. **Déléguer** : Collecte les données :
   - 523 PME industrielles trouvées
   - 8 procédures en cours détectées
   - 12 articles de presse analysés

4. **Synthétiser** : Analyse et croise les informations :
   - Identifie 15 entreprises à surveiller
   - Les classe par niveau de risque
   - Explique pourquoi chacune est à risque

5. **Apprendre** : Si vous lui dites qu'une entreprise n'est pas vraiment à risque, il ajustera ses futurs calculs

---

## Les Sources de Données

TAJINE ne "devine" pas - il s'appuie sur des **sources officielles et vérifiables** :

### Données Officielles (100% fiables)

| Source | Ce qu'elle contient |
|--------|---------------------|
| **SIRENE** (INSEE) | Toutes les entreprises françaises, leur adresse, activité, taille |
| **BODACC** | Annonces légales : créations, faillites, changements |
| **BOAMP** | Marchés publics attribués |
| **DVF** | Prix des transactions immobilières |
| **INSEE** | Statistiques population, emploi, revenus |

### Données Complémentaires

| Source | Ce qu'elle apporte |
|--------|---------------------|
| **Presse locale** | Signaux faibles, annonces économiques |
| **Pappers** | Informations sur les dirigeants |
| **Géorisques** | Risques environnementaux |

### Données Inférées (avec précaution)

Certaines données n'existent pas publiquement. TAJINE peut les **estimer** en précisant toujours :
- Que c'est une estimation
- La méthode utilisée
- Le niveau de confiance

Exemple : Le chiffre d'affaires d'une entreprise n'est pas public, mais TAJINE peut l'estimer à partir de son effectif et de son secteur.

---

## Les 5 Niveaux d'Analyse

TAJINE analyse les données à travers 5 niveaux de profondeur :

### 1. Découverte
**"Que se passe-t-il ?"**
- Liste les faits bruts
- Détecte les anomalies évidentes

### 2. Analyse Causale
**"Pourquoi ?"**
- Cherche les causes des phénomènes observés
- Identifie les liens entre événements

### 3. Scénarios
**"Que pourrait-il se passer ?"**
- Projette plusieurs futurs possibles
- Évalue la probabilité de chaque scénario

### 4. Stratégie
**"Que faire ?"**
- Propose des actions concrètes
- Priorise les interventions

### 5. Théorique
**"Quelles leçons en tirer ?"**
- Identifie les patterns récurrents
- Enrichit la connaissance pour le futur

---

## Fiabilité et Transparence

### Le Système Anti-Hallucination

TAJINE est conçu pour **ne jamais inventer** d'informations. Pour chaque affirmation :

1. **Source citée** : D'où vient l'information ?
2. **Score de confiance** : À quel point est-ce fiable ?
3. **Limitations** : Qu'est-ce qu'on ne sait pas ?

### Les Niveaux de Confiance

| Score | Niveau | Signification |
|-------|--------|---------------|
| 85-100% | TRÈS HAUTE | Donnée officielle récente |
| 70-84% | HAUTE | Sources multiples concordantes |
| 50-69% | MOYENNE | Estimation avec méthode solide |
| 30-49% | BASSE | Hypothèse à vérifier |
| <30% | TRÈS BASSE | Information insuffisante |

### Ce que TAJINE dit toujours :

- ✅ "Voici ce que j'ai trouvé" (faits)
- ✅ "Voici ce que j'en déduis" (analyse)
- ✅ "Voici ce que je ne sais pas" (limitations)
- ✅ "Voici mes sources" (traçabilité)

---

## Cas d'Usage Typiques

### 1. Alerte Risque Entreprise

> **Besoin** : Être alerté avant qu'une entreprise importante ne fasse faillite

**TAJINE détecte :**
- Retards de paiement signalés
- Articles de presse négatifs
- Baisse d'activité du secteur
- Départ de dirigeants

**TAJINE alerte :**
"L'entreprise X présente un risque élevé (68%). Signaux : procédure collective chez 2 sous-traitants, 3 articles négatifs ce mois-ci."

### 2. Diagnostic Territorial

> **Besoin** : Comprendre la santé économique d'une intercommunalité

**TAJINE analyse :**
- Évolution du nombre d'entreprises
- Créations vs radiations
- Secteurs en croissance/déclin
- Comparaison avec territoires similaires

**TAJINE produit :**
Un rapport avec indicateurs, tendances, et recommandations.

### 3. Détection d'Opportunités

> **Besoin** : Identifier les secteurs émergents

**TAJINE surveille :**
- Créations d'entreprises par secteur
- Levées de fonds annoncées
- Recrutements en hausse
- Tendances dans la presse spécialisée

**TAJINE signale :**
"Émergence détectée : 12 startups AgriTech créées dans la région ces 6 mois (+150% vs année précédente)"

---

## Utilisation Pratique

### Commandes Disponibles

```bash
# Voir le statut du système
mptoo tajine status

# Lancer une analyse
mptoo tajine analyze "Votre question ici"

# Exemples de questions
mptoo tajine analyze "Analyse le secteur tech dans l'Hérault"
mptoo tajine analyze "Quelles entreprises sont à risque dans le 34 ?"
mptoo tajine analyze "Compare l'attractivité de Montpellier vs Toulouse"
```

### Options Utiles

| Option | Description |
|--------|-------------|
| `--territory 34` | Spécifier un département |
| `--sector tech` | Filtrer par secteur |
| `--verbose` | Afficher le détail du processus |
| `--json` | Sortie au format JSON |

### Exemple Complet

```bash
mptoo tajine analyze "Analyse le potentiel tech dans l'Hérault" \
  --territory 34 \
  --sector tech \
  --verbose
```

---

## Questions Fréquentes

### TAJINE peut-il se tromper ?

Oui, comme tout système d'analyse. C'est pourquoi :
- Chaque résultat inclut un score de confiance
- Les limitations sont toujours mentionnées
- Les sources sont citées pour vérification

### Les données sont-elles à jour ?

- **APIs officielles** : données de J-1 à J-7
- **Presse** : temps réel
- **Statistiques INSEE** : annuelles (avec retard)

### TAJINE remplace-t-il les analystes humains ?

Non. TAJINE est un **outil d'aide à la décision**. Il :
- Automatise la collecte de données
- Détecte les signaux faibles
- Propose des analyses

Mais **l'humain décide** et peut corriger TAJINE pour l'améliorer.

### Comment TAJINE protège les données ?

- TAJINE n'utilise que des données **publiques ou open data**
- Aucune donnée personnelle n'est collectée
- Conforme RGPD

---

## Glossaire

| Terme | Définition |
|-------|------------|
| **Signal faible** | Information émergente qui annonce une tendance future |
| **PPDSL** | Perceive-Plan-Delegate-Synthesize-Learn : le cycle de traitement |
| **Knowledge Graph** | Base de données qui stocke les entités et leurs relations |
| **Conformal Prediction** | Méthode statistique qui donne des intervalles de confiance calibrés |
| **SIRENE** | Système national d'identification des entreprises (INSEE) |
| **BODACC** | Bulletin Officiel des Annonces Civiles et Commerciales |
| **NAF** | Nomenclature d'Activités Française (code secteur) |

---

## Pour Aller Plus Loin

- **Documentation technique** : `docs/plans/2025-12-14-tajine-documentation-index.md`
- **Architecture** : `docs/plans/2025-12-14-tajine-agentic-architecture-design.md`
- **Moteur cognitif** : `docs/plans/2025-12-13-tajine-cognitive-engine-design.md`

---

*TAJINE - Intelligence Territoriale Augmentée*
*Projet MPtoO-V2*
