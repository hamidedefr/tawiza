# Tawiza - Repo Public (Open Source)

## Architecture dual-repo

Ce repo (`tawiza/tawiza`) est la version **open source** du projet.
Le repo prive est `hamidedefr/MPtoO-v2`.

```
tawiza/tawiza        → Public, open source (MIT), visible par tous
hamidedefr/MPtoO-v2  → Prive, premium, entreprise & conseil
```

## Strategie de separation (decidee 2026-03-23)

**Ce qui est deja dans ce repo reste et est maintenu.**
Bugfixes, mises a jour de securite, correctifs de deps : oui.
Nouvelles features premium : non, ca va dans MPtoO-V2.

### Ce repo contient (baseline figee)

- Backend FastAPI complet (endpoints TAJINE, conversations, export, sources, watcher, etc.)
- Agent TAJINE (cycle PPDSL, 5 niveaux cognitifs, Data Hunter, planning, RAG)
- 21 adaptateurs de sources de donnees (SIRENE, BODACC, DVF, INSEE, France Travail, etc.)
- 28 services applicatifs (scoring, correlation, relations, alertes, etc.)
- Knowledge Graph (Neo4j, algorithmes)
- Crawler adaptatif (MAB, workers)
- Browser agents (Playwright, Camoufox, stealth)
- CAMEL workforce (12 agents)
- Dashboard Next.js (7 pages)
- CLI/TUI (Typer + Textual)
- Collecteur unifie (14 API collectors + 2 crawlers)
- Detection d'anomalies (Isolation Forest, DBSCAN)
- Docker-compose pour self-hosting
- Tests (200 fichiers, 3389 tests)

### Ce qui va dans MPtoO-V2 (tout le nouveau)

- Nouvelles pages frontend premium (simulation, investigation avancee, etc.)
- Nouveaux algorithmes de scoring/analyse
- Pipeline de fine-tuning et modeles entraines
- Configs GPU, benchmarks, donnees d'entrainement
- Documents de design et strategie (88 docs)
- Scripts de deploiement et infra interne
- Donnees persistantes (trust scores, memoire episodique)
- Nouveaux agents et outils
- Toute feature qui n'existait pas au 2026-03-23

### Comment decider pour un nouveau fichier

```
Le fichier existait deja dans ce repo au 2026-03-23 ?
  OUI → bugfix/maintenance ici, OK
  NON → ca va dans MPtoO-V2

C'est un bugfix ou patch de securite sur du code existant ?
  OUI → ici
  NON → MPtoO-V2

C'est une nouvelle feature, un nouvel algo, une nouvelle page ?
  → MPtoO-V2, toujours
```

## Regles absolues

1. Ne JAMAIS ajouter de nouvelles features premium dans ce repo
2. Ne JAMAIS referencer MPtoO-V2, hamidedefr, ou des chemins internes
3. Ne JAMAIS hardcoder des secrets, tokens, ou IPs de serveur
4. Ne JAMAIS publier des donnees brutes ou intermediaires
5. Maintenance seulement : bugfixes, securite, mise a jour deps

## Conventions

### Code
- Python 3.12+, FastAPI, SQLAlchemy async
- Next.js 15, TypeScript, Tailwind CSS, shadcn/ui
- Commits en francais, courts et directs
- Pas de vocabulaire marketing ("propulse par l'IA", "cognitif", "proactif")

### Documentation
- Pas d'em dashes, pas de smart quotes
- Ton sobre et factuel
- Chiffres reels, pas gonfles

## Mainteneur

@hamidedefr
