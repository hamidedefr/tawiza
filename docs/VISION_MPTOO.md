# MPtoO-V2 — Ce que j'ai compris

*Document de synthèse — Syl, 6 février 2026*

---

## 🎯 Le problème qu'on résout

**Constat de terrain (validé avec Hamide) :**
- Les collectivités territoriales françaises manquent de visibilité sur leur économie locale
- Les données INSEE ont 1-3 ans de retard
- Elles bricolent avec Excel, des prestataires coûteux, ou des outils abandonnés
- Les décideurs (Régions, Ministères) n'ont pas d'outil unifié pour piloter

**La douleur :**
> "Je suis élu/technicien d'une collectivité, je veux savoir si mon territoire va bien économiquement, quels secteurs souffrent, et anticiper les crises — sans attendre 2 ans les stats INSEE."

---

## 💡 Notre proposition de valeur

**MPtoO = Intelligence Territoriale Temps Réel**

On croise des données publiques françaises (BODACC, SIRENE, France Travail, INSEE, DVF...) pour produire :

1. **Un indice de vitalité** par territoire (département, commune)
2. **Des alertes précoces** (entreprises en difficulté, secteurs en crise)
3. **Des analyses sectorielles** (qui crée, qui ferme, dans quel domaine)
4. **Des rapports automatiques** pour les décideurs

**Différenciation vs INSEE :**
- Temps réel (J+1) vs années de retard
- Croisement multi-sources vs silos
- Alertes proactives vs consultation passive
- IA qui explique vs tableaux bruts

---

## 🏗️ Architecture actuelle

```
┌─────────────────────────────────────────────────────────┐
│                      FRONTEND                           │
│                  (Next.js 14 / React)                   │
│         Dashboard, cartes, widgets comparatifs          │
└─────────────────────┬───────────────────────────────────┘
                      │ REST API
┌─────────────────────▼───────────────────────────────────┐
│                      BACKEND                            │
│                (FastAPI / Python 3.13)                  │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ Territorial │  │   TAJINE    │  │   Reports   │     │
│  │  Metrics    │  │   Agent     │  │  Generator  │     │
│  │  Collector  │  │ (narratif)  │  │             │     │
│  └──────┬──────┘  └──────┬──────┘  └─────────────┘     │
│         │                │                              │
│  ┌──────▼────────────────▼──────────────────────┐      │
│  │              ADAPTERS (datasources)           │      │
│  │  BODACC │ SIRENE │ France Travail │ INSEE    │      │
│  │   DVF   │  BAN   │    BOAMP       │ GDELT    │      │
│  └──────────────────────────────────────────────┘      │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                    STOCKAGE                             │
│   SQLite (historique)  │  Ollama (LLM local)           │
│   ChromaDB (vectors)   │  Cache mémoire                │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Données actuellement intégrées

| Source | Données | Fraîcheur | Usage |
|--------|---------|-----------|-------|
| **BODACC** | Créations, fermetures, procédures | J+1 | Flux entreprises |
| **SIRENE** | Stock établissements | J+1 | Base référentiel |
| **France Travail** | Offres emploi, chômage | Temps réel | Tension emploi |
| **INSEE** | Taux chômage, population | Trimestriel | Contexte socio |
| **DVF** | Transactions immobilières | Mensuel | Attractivité |
| **BAN** | Géolocalisation adresses | Stable | Cartographie |
| **BOAMP** | Marchés publics | J+1 | Investissement public |

---

## 🧮 Algo actuel (vitalité)

**Formule simple à pondérations :**
```
Score = 50 (base)
  + (créations - fermetures) / stock × 750    # ±15 pts
  - procédures / stock × 1000                  # -10 pts max
  + offres_emploi / stock × 100                # +10 pts max
  + (7 - taux_chômage) × 1.5                   # ±10 pts
  + transactions_immo / population × 500       # +5 pts max
```

**Limites :**
- Pas de prédiction (juste état actuel)
- Pas de causalité (corrélation ≠ cause)
- Pondérations arbitraires (pas calibrées sur données réelles)

---

## ❓ Questions ouvertes

### Produit
- **Cible exacte ?** Collectivités ? Cabinets conseil ? Journalistes data ?
- **Format livrable ?** Dashboard web ? API ? Rapports PDF ? Alertes email ?
- **Modèle économique ?** SaaS ? Prestation ? Open data enrichi ?

### Technique
- **Micro-signaux ?** Cours matières premières, Google Trends, satellites...
- **Prédiction ML ?** Besoin de 6+ mois d'historique d'abord
- **Multi-agent évolué ?** S'inspirer de ChatDev pour TAJINE ?

### Données
- **Quelles sources manquent ?** Banque de France ? Urssaf ? Impôts ?
- **Granularité ?** Département OK, mais commune ? EPCI ? Bassin d'emploi ?
- **Historique ?** Combien de profondeur ? Coût stockage ?

---

## 🛤️ Ce que je pensais être la roadmap

1. ✅ **V1** — Vitalité simple (BODACC + SIRENE) — FAIT
2. ✅ **V2** — Multi-sources (France Travail, INSEE, DVF) — FAIT
3. 🔄 **V3** — Micro-signaux (commodities, trends) — EN RÉFLEXION
4. ⏳ **V4** — Prédiction ML (après collecte historique)
5. ⏳ **V5** — Multi-agent intelligent (TAJINE évolué)

---

## 🤔 Ce que je ne sais pas encore

1. **Qui est le client final ?** (et sa vraie douleur quotidienne)
2. **Quel niveau de précision est "suffisant" ?** (80% fiable = OK ?)
3. **Budget/contraintes ?** (tout local ou cloud possible ?)
4. **Échéance ?** (MVP pour quand ?)
5. **Équipe ?** (juste nous deux ou d'autres contributeurs ?)

---

*À compléter ensemble — ce doc est un point de départ, pas une vérité.*
