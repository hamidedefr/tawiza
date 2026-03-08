# Catalogue des Sources de Données MPtoO

*Dernière mise à jour : 2026-02-05*

---

## ✅ Intégrées (adaptateurs existants)

| Source | Adaptateur | Données | Fraîcheur | Auth |
|--------|-----------|---------|-----------|------|
| SIRENE | `sirene.py` | Entreprises, établissements | J+1 à J+7 | Token INSEE |
| BODACC | `bodacc.py` | Annonces légales, défaillances | Temps réel | Non |
| BOAMP | `boamp.py` | Marchés publics | Temps réel | Non |
| BAN | `ban.py` | Adresses, géocodage | À jour | Non |
| INSEE Local | `insee_local.py` | Stats socio-éco | Retard 1-3 ans | OAuth2 |
| DVF | `dvf.py` | Transactions immobilières | ~6 mois | Non |
| France Travail | `france_travail.py` | Emploi, offres, stats chômage | Hebdo | Token |
| OFGL | `ofgl.py` | Finances collectivités | Annuel | Non |
| Subventions | `subventions.py` | Aides publiques | Variable | Non |
| DBnomics | `dbnomics.py` | Agrégateur stats économiques | Variable | Non |
| Google News | `google_news.py` | Actualités | Temps réel | Non |
| GDELT | `gdelt.py` | Événements médias mondiaux | Temps réel | Non |
| Google Trends | `pytrends_adapter.py` | Tendances recherche | Temps réel | Non |

---

## 🎯 À intégrer (priorité haute)

### Données entreprises enrichies

| Source | Données | Intérêt micro-signaux | URL |
|--------|---------|----------------------|-----|
| **INPI Open Data** | Brevets, marques, comptes annuels | Innovation, santé financière | data.inpi.fr |
| **Urssaf Open Data** | Effectifs salariés par zone | Emploi temps réel | open.urssaf.fr |
| **Annuaire Entreprises** | Recherche simplifiée, dirigeants | Enrichissement | annuaire-entreprises.data.gouv.fr |
| **API Géo** | Communes, EPCI, contours | Zonage précis | geo.api.gouv.fr |

### Signaux économiques avancés

| Source | Données | Intérêt micro-signaux |
|--------|---------|----------------------|
| **FRED** | Indicateurs macro mondiaux | Contexte global |
| **Eurostat** | Stats UE comparatives | Benchmark européen |
| **ECB** | Taux, crédit, monnaie | Contexte financier |

---

## 🔮 À explorer (signaux faibles / alternative data)

| Source | Signal potentiel |
|--------|------------------|
| **LinkedIn Jobs** (scraping) | Recrutements = croissance |
| **Google Maps reviews** | Activité commerces, fermetures |
| **Indeed/HelloWork** | Offres emploi locales |
| **Societe.com** (scraping) | Comptes, dirigeants |
| **Presse locale RSS** | Événements, annonces |
| **Permis de construire** | Projets immobiliers futurs |
| **Cadastre/DVF croisé** | Dynamique foncière |
| **Trafic routier** (Waze/TomTom) | Activité économique |
| **Consommation électrique** (RTE) | Activité industrielle |

---

## 🧠 Logique Micro-Signaux TAJINE

### Principe
> Croiser des signaux faibles de sources différentes pour détecter des tendances AVANT qu'elles soient visibles dans les stats officielles.

### Catalogue de Patterns (35+)

---

#### 🔴 PATTERNS CRISE / ALERTE (1-10)

**1. Crise sectorielle locale**
```
Offres emploi ↓ secteur X + Procédures BODACC ↑ même secteur
+ Google Trends "licenciement/chômage" + ville ↑
→ Alerte crise sectorielle imminente
```

**2. Défaillance en cascade**
```
Défaillance grosse entreprise (>50 salariés)
+ Sous-traitants même zone identifiés SIRENE
+ Retards paiement BODACC sous-traitants
→ Risque effet domino
```

**3. Désertification commerciale**
```
Fermetures commerces BODACC centre-ville > seuil
+ Locaux vacants (croisement cadastre)
+ Baisse Google Trends commerces locaux
→ Alerte dévitalisation centre
```

**4. Dépendance employeur unique**
```
1 entreprise > 30% emploi zone (SIRENE/Urssaf)
+ Signaux faibles négatifs sur cette entreprise
→ Risque territorial critique
```

**5. Fuite des talents**
```
Offres cadres ↓ + Créations entreprises innovantes ↓
+ Transactions immo jeunes actifs ↓
→ Perte attractivité qualifiée
```

**6. Crise immobilière locale**
```
Transactions DVF ↓↓ + Prix m² stagnant
+ Permis construire ↓ + Offres agences immo ↑↑
→ Retournement marché immobilier
```

**7. Hémorragie entrepreneuriale**
```
Radiations SIRENE > Créations (ratio < 0.8)
+ Durée vie moyenne entreprises ↓
→ Environnement hostile entrepreneurs
```

**8. Crise agricole**
```
Exploitations agricoles ↓↓
+ Prix terres agricoles ↓
+ Procédures collectives agriculteurs ↑
→ Crise structurelle agricole
```

**9. Surendettement territorial**
```
Procédures surendettement Banque France ↑
+ Impayés loyers ↑
+ Inscriptions RSA ↑
→ Précarisation population
```

**10. Obsolescence industrielle**
```
Âge moyen équipements ↑
+ Investissements industriels ↓
+ Productivité stagnante
→ Risque décrochage industriel
```

---

#### 🟢 PATTERNS DYNAMISME / OPPORTUNITÉ (11-20)

**11. Zone en décollage**
```
Créations SIRENE ↑ + Recrutements ↑
+ Transactions DVF ↑ + Prix m² ↑ modéré
→ Territoire en croissance
```

**12. Cluster émergent**
```
Créations même code NAF concentrées géographiquement
+ Brevets INPI même domaine ↑
+ Recrutements spécialisés ↑
→ Cluster sectoriel en formation
```

**13. Attractivité résidentielle**
```
Transactions DVF ↑ (acheteurs hors zone)
+ Créations auto-entrepreneurs ↑
+ Recherches Google "vivre à [ville]" ↑
→ Nouvelle attractivité territoriale
```

**14. Boom entrepreneurial**
```
Créations SIRENE ↑↑ + dont primo-créateurs ↑
+ Formations création entreprise ↑
+ Coworking/pépinières remplissage ↑
→ Dynamique entrepreneuriale forte
```

**15. Réindustrialisation**
```
Créations NAF industrie ↑ + Permis construire industriels ↑
+ Offres emploi production ↑
→ Renaissance industrielle locale
```

**16. Économie verte émergente**
```
Créations NAF énergie/environnement ↑
+ Brevets INPI cleantech ↑
+ Marchés publics BOAMP transition écologique ↑
→ Positionnement économie verte
```

**17. Pôle santé/silver économie**
```
Créations NAF santé/médico-social ↑
+ Population >65 ans ↑
+ Équipements santé ↑
→ Spécialisation silver économie
```

**18. Hub logistique**
```
Créations NAF transport/logistique ↑
+ Surfaces entrepôts ↑
+ Emplois logistique ↑
→ Émergence pôle logistique
```

**19. Tourisme en croissance**
```
Nuitées ↑ + Créations hébergement/restauration ↑
+ Recherches Google tourisme [zone] ↑
+ Événements locaux ↑
→ Dynamique touristique positive
```

**20. Tech hub émergent**
```
Créations NAF numérique ↑↑
+ Levées de fonds startups locales
+ Recrutements dev/data ↑
+ Écoles numériques présentes
→ Écosystème tech en formation
```

---

#### 🟡 PATTERNS MUTATION / TRANSFORMATION (21-26)

**21. Mutation centre → périphérie**
```
Fermetures commerce centre ↑ + Créations zone commerciale ↑
+ Permis construire périphérie ↑
→ Étalement commercial en cours
```

**22. Tertiarisation économie**
```
Emplois industrie ↓ + Emplois services ↑
+ Surfaces bureaux ↑ / surfaces industrielles ↓
→ Mutation vers économie de services
```

**23. Gentrification**
```
Prix DVF ↑↑ rapide + Commerces "premium" ↑
+ Population CSP+ ↑ + Loyers ↑
→ Gentrification en cours
```

**24. Transition agricole**
```
Exploitations conventionnelles ↓ + Bio/circuits courts ↑
+ Marchés publics cantines bio ↑
→ Mutation modèle agricole
```

**25. Vieillissement économique**
```
Dirigeants >55 ans / total dirigeants ↑
+ Transmissions < créations
+ Offres reprise ↑
→ Enjeu succession entrepreneuriale
```

**26. Économie de plateforme**
```
Auto-entrepreneurs livraison/VTC ↑↑
+ Emplois salariés mêmes secteurs ↓
→ Uberisation économie locale
```

---

#### 🔵 PATTERNS EMPLOI / SOCIAL (27-30)

**27. Tension métiers**
```
Offres emploi métier X >> demandeurs
+ Durée moyenne offres ↑↑
+ Salaires proposés ↑
→ Pénurie main d'œuvre critique
```

**28. Inadéquation formation**
```
Offres emploi secteur X ↑
+ Formations locales secteur X absentes
+ Demandeurs emploi autres secteurs ↑
→ Besoin adaptation formation
```

**29. Précarisation emploi**
```
CDI ↓ + CDD/intérim ↑
+ Auto-entrepreneurs "contraints" ↑
+ Temps partiel subi ↑
→ Fragilisation emploi local
```

**30. Exode pendulaire**
```
Population active > emplois locaux
+ Trafic routier sortant ↑↑
+ Créations entreprises stagnant
→ Territoire dortoir
```

---

#### 🟣 PATTERNS MARCHÉS PUBLICS (31-33)

**31. Dépendance marchés publics**
```
Entreprises avec >50% CA public
+ Concentration sur peu d'entreprises
→ Risque si baisse commande publique
```

**32. Opportunité BOAMP**
```
Marchés publics secteur X ↑↑
+ Peu d'entreprises locales secteur X
→ Opportunité création/implantation
```

**33. Stress budgétaire collectivité**
```
Dette collectivité ↑ (OFGL)
+ Investissement ↓ + Reports marchés
→ Difficulté financière collectivité
```

---

#### ⚪ PATTERNS INNOVATION (34-35)

**34. Innovation souterraine**
```
Brevets INPI domaine X ↑ (avant créations)
+ Publications recherche locale ↑
+ Thèses CIFRE ↑
→ Innovation pré-commerciale
```

**35. Disruption sectorielle**
```
Startups nouveau modèle ↑
+ Entreprises traditionnelles en difficulté
+ Recherches Google nouveau modèle ↑
→ Disruption en cours
```

---

#### 🌡️ INDICES SYNTHÉTIQUES (36-40)

**36. Indice Vitalité Territoriale**
```
= (Créations - Défaillances) / Stock × 100
+ Évolution emploi × 0.3
+ Dynamique immo × 0.2
→ Score 0-100 santé globale
```

**37. Indice Résilience**
```
= Diversité sectorielle (Herfindahl inversé)
× (1 - Dépendance top 5 employeurs)
× Formation population active
→ Capacité absorber chocs
```

**38. Indice Attractivité**
```
= Solde migratoire entreprises
+ Solde migratoire population
+ Accessibilité transports
→ Pouvoir d'attraction
```

**39. Indice Innovation**
```
= Brevets / 1000 entreprises
+ Startups / 1000 entreprises
+ Emplois R&D / total emplois
→ Potentiel innovation
```

**40. Indice Transition Écologique**
```
= Créations éco-activités / total
+ Marchés publics verts / total
+ Évolution conso énergie / PIB local
→ Avancement transition
```

---

### Architecture proposée

```
┌─────────────────────────────────────────────────┐
│                   TAJINE                        │
├─────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │ Collecteurs │  │ Analyseurs  │  │ Alertes │ │
│  │ (adapters)  │→ │ (patterns)  │→ │ (règles)│ │
│  └─────────────┘  └─────────────┘  └─────────┘ │
│         ↓                ↓              ↓      │
│  ┌─────────────────────────────────────────┐   │
│  │         Mémoire vectorielle             │   │
│  │   (historique + embeddings + trends)    │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

### Métriques à construire

| Métrique | Sources | Calcul |
|----------|---------|--------|
| Vitalité économique | SIRENE + BODACC | (créations - défaillances) / stock |
| Tension emploi | France Travail | offres / demandeurs |
| Dynamique immo | DVF + permis | prix m² + volume + projets |
| Innovation | INPI | brevets + marques / entreprises |
| Dépendance sectorielle | SIRENE | concentration NAF |

---

## Prochaines étapes

1. [ ] Créer adaptateurs INPI, Urssaf, API Géo
2. [ ] Définir 5 patterns micro-signaux prioritaires
3. [ ] Implémenter scoring de vitalité territoriale
4. [ ] Tester sur 3 territoires pilotes (1 rural, 1 urbain, 1 péri-urbain)
