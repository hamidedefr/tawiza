# 🚀 MPtoO-V2 Production Roadmap

**Deadline:** 1 semaine (7 février 2026)
**Status:** En développement → Production

---

## 📋 Checklist Production

### P0 - Critiques (Jour 1-2)

- [ ] **Données réelles** — Remplacer les trends synthétiques
- [ ] **Sécurité** — Audit credentials, CORS, rate limiting
- [ ] **Stabilité** — Services qui ne crash pas
- [ ] **Logs** — Logging structuré pour debug

### P1 - Importants (Jour 3-4)

- [ ] **Performance** — Cache Redis, lazy loading
- [ ] **Error handling** — Messages utilisateur clairs
- [ ] **Tests** — Coverage minimum 15%
- [ ] **Documentation** — API docs complète

### P2 - Nice to have (Jour 5-6)

- [ ] **UI Polish** — Responsive, loading states
- [ ] **Monitoring** — Health checks, métriques
- [ ] **Backup** — Export données utilisateur

### P3 - Jour 7

- [ ] **Deployment** — Docker compose production
- [ ] **Tests finaux** — Smoke tests complets
- [ ] **Documentation** — Guide utilisateur

---

## 🔧 Issues Connues

| Issue | Sévérité | Fix |
|-------|----------|-----|
| Trends synthétiques | ⚠️ High | Stocker historique DB |
| Embeddings 404 | ⚠️ Medium | Config nomic-embed |
| CAMEL agents manquants | 🟡 Low | Optionnel |
| Synthesize signature | 🟡 Low | Fix méthode |
| Services crash en background | ⚠️ High | Systemd services |

---

## 🏗️ Architecture Production

```
┌─────────────────────────────────────────────────────┐
│                    NGINX (reverse proxy)            │
│                    SSL + Rate Limiting              │
├──────────────────────┬──────────────────────────────┤
│   Frontend :3000     │      Backend :8000           │
│   (Next.js SSR)      │      (FastAPI + TAJINE)      │
├──────────────────────┴──────────────────────────────┤
│                    Redis (cache)                    │
├─────────────────────────────────────────────────────┤
│                    PostgreSQL (data)                │
├─────────────────────────────────────────────────────┤
│                    Ollama :11434 (GPU)              │
│                    qwen3:14b + nomic-embed          │
└─────────────────────────────────────────────────────┘
```

---

## 📊 APIs Externes - Status

| API | Status | Credentials |
|-----|--------|-------------|
| SIRENE (INSEE) | ✅ OK | .env |
| BODACC | ✅ OK | Public |
| BOAMP | ⚠️ À tester | .env |
| DVF | ⚠️ À tester | Public |
| France Travail | ⚠️ À tester | .env |
| BAN (Adresses) | ✅ OK | Public |

---

## 🎯 Objectifs Semaine

### Lundi (Jour 1)
- [ ] Systemd services (backend/frontend persistants)
- [ ] Fix données synthétiques → historique DB
- [ ] Audit sécurité credentials

### Mardi (Jour 2)
- [ ] Tests APIs externes (toutes)
- [ ] Error handling unifié
- [ ] Logging structuré (JSON)

### Mercredi (Jour 3)
- [ ] Cache Redis pour APIs
- [ ] Performance TAJINE (< 20s)
- [ ] Tests unitaires critiques

### Jeudi (Jour 4)
- [ ] UI: loading states, erreurs
- [ ] Documentation API (OpenAPI)
- [ ] Tests d'intégration

### Vendredi (Jour 5)
- [ ] Docker compose production
- [ ] CI/CD basique
- [ ] Monitoring health

### Samedi (Jour 6)
- [ ] Tests end-to-end
- [ ] Fix bugs remontés
- [ ] Documentation utilisateur

### Dimanche (Jour 7)
- [ ] Deployment final
- [ ] Smoke tests
- [ ] Handover documentation
