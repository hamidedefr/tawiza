# Plan Prochaine Session - MPtoO-V2

**Date**: 2026-03-05
**Etat**: 1.08M signaux, 13 sources, 5 jobs scheduler, CrawlIntel integre

---

## A) Reparer les 6 sources offline (priorite haute)

**Impact**: Recuperer ~30K signaux frais, couverture territoriale complete

### Sources offline depuis le 21/02
| Source | Derniere collecte | Signaux | Action probable |
|--------|-------------------|---------|-----------------|
| Sitadel | 21/02 | 16.6K | Verifier API SDES, token expire ? |
| CAF | 21/02 | 9.7K | Verifier endpoint, peut etre rate limited |
| DGFiP | 21/02 | 1K | API tres restrictive, verifier accreditation |
| Google Trends | 21/02 | 481 | pytrends bloque ? Proxy necessaire ? |
| URSSAF | 21/02 | 400 | Verifier API open data URSSAF |
| Education Nationale | 21/02 | 86 | Source mineure, basse priorite |

### Sources degraded
| Source | Etat | Action |
|--------|------|--------|
| SIRENE | Degraded | Verifier rate limiting INSEE API |
| INSEE | Degraded | Token API ? Quota atteint ? |
| DVF | Degraded | API data.gouv.fr, verifier parsing |
| OFGL | Degraded | Donnees annuelles, normal si pas de MAJ |

### Diagnostic
```bash
# Pour chaque source, verifier:
# 1. L'adaptateur peut-il se connecter ?
curl -s http://localhost:8000/api/collector/run/{source}?code_dept=75
# 2. Les logs d'erreur
journalctl -u mptoo-backend | grep -i "{source}.*error"
# 3. Le health check de l'adaptateur
python3 -c "from src.infrastructure.datasources.adapters.{source} import *; ..."
```

---

## B) Lancer TAJINE en production (priorite haute)

**Impact**: Activer le coeur du systeme - analyses territoriales reelles

### Constat
- 0 analyses TAJINE executees
- trust = 0.00
- Le frontend ai-chat et tajine sont connectes mais jamais utilises

### Actions
1. **Test TAJINE direct** via API:
   ```bash
   curl -X POST http://localhost:8000/api/v1/tajine/analyze \
     -H "Content-Type: application/json" \
     -d '{"query": "Analyse economique du departement 75", "dept": "75", "level": "discovery"}'
   ```
2. **Verifier la connexion Ollama** pour TAJINE (qwen3.5:27b ou autre modele)
3. **Lancer une analyse par departement** sur les 18 departements monitores
4. **Verifier le WebSocket** pour le suivi en temps reel
5. **Tester le chat TAJINE** depuis le frontend

### Risques
- Le cycle PPDSL (5 phases) peut etre lent avec qwen3.5:27b (thinking mode)
- Le TrustManager demarre a 0, les premieres analyses seront moins fiables

---

## C) Diagnostiquer la detection d'anomalies ML (priorite moyenne)

**Impact**: Activer les alertes automatiques sur les signaux croises

### Constat
- Table `anomalies` = 0 rows
- Job `cross_source_detection` tourne quotidiennement a 7h
- Avec 1.08M signaux, il devrait y avoir des anomalies

### Diagnostic
1. **Verifier les logs du job**:
   ```bash
   journalctl -u mptoo-backend | grep -i "cross.source\|micro.signal"
   ```
2. **Lancer manuellement**:
   ```bash
   curl -X POST http://localhost:8000/api/collector/run/cross_source
   ```
3. **Verifier le module**:
   - `src/collector/crawling/crossref.py` - seuils trop stricts ?
   - Fenetre 7 jours vs baseline 30 jours - suffisant ?
4. **Tester la detection ML**:
   ```bash
   curl -X POST http://localhost:8000/api/collector/ml/run-detection
   ```
5. **Verifier Isolation Forest / HDBSCAN** parametrage

### Hypotheses
- Les signaux sont trop uniformes (pas assez de variance inter-sources)
- Le seuil de detection est trop conservateur
- Le module ne trouve pas assez de signaux croises (source A + source B meme dept meme periode)

---

## D) Verifier les pages frontend (priorite moyenne)

**Impact**: UX coherente, pas de pages vides en production

### Pages a auditer
| Page | Route | Statut suspect |
|------|-------|----------------|
| Predictions | /dashboard/predictions | Donnees reelles ou mockees ? |
| Comparateur | /dashboard/compare | Fonctionnel ? |
| EPCI / Communes | /dashboard/epci | Donnees dispo ? |
| Alertes | /dashboard/alertes | Connecte aux anomalies (0) ? |
| Investigation | /dashboard/investigation | Relations graph ? |
| Signaux | /dashboard/signals | Liste les 1M+ signaux ? |
| Fine-Tuning | /dashboard/fine-tuning | OumiBridge connecte ? |

### Actions
1. Naviguer chaque page et verifier les donnees affichees
2. Identifier les pages avec placeholder/mock data
3. Connecter aux vraies APIs si necessaire
4. Supprimer ou masquer les pages non fonctionnelles

---

## E) Nettoyage technique (priorite basse)

- **GlitchTip/Sentry**: port 1337 unreachable, erreurs en boucle toutes les 2min dans les logs. Desactiver ou reparer
- **Tests CrawlIntel**: ecrire tests unitaires pour le pipeline
- **40 TODO/FIXME** dans le codebase (identifies lors de l'audit)
- **tajine_agent.py**: 1992 lignes, a refactorer

---

## Ordre recommande

1. **A** (sources offline) → impact immediat sur la qualite des donnees
2. **B** (TAJINE production) → active le coeur du systeme
3. **C** (anomalies ML) → donne du sens aux donnees collectees
4. **D** (frontend) → UX coherente pour la demo/utilisation

Duree estimee: 2-3 sessions selon la complexite des bugs sources.
