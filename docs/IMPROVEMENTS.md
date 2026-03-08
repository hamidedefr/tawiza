# Améliorations TAJINE - 2026-01-31

## État actuel ✅

| Composant | Status | Notes |
|-----------|--------|-------|
| GPU AMD RX 7900 XTX | ✅ Fonctionnel | 24GB VRAM via Vulkan |
| Ollama qwen3:14b | ✅ Fonctionnel | Mode rapide |
| Ollama nomic-embed-text | ✅ Installé | Pour embeddings |
| TAJINE Perceive | ✅ Fonctionne | ~10s |
| TAJINE Plan | ✅ Fonctionne | ~24s |
| TrustManager | ✅ Persistant | data/tajine/trust.json |
| EpisodicStore | ✅ Initialisé | data/tajine/episodic_memory |

## Problèmes identifiés 🔧

### 1. Embeddings 404
- **Cause**: Le retriever utilise `/api/embeddings` mais n'a pas de modèle configuré
- **Fix**: Configurer `nomic-embed-text` dans le retriever
- **Fichier**: `src/infrastructure/agents/tajine/memory/retriever.py`

### 2. CAMEL agents manquants
- **Cause**: Module `camel` non installé
- **Impact**: Fonctionnel mais sans agents CAMEL (DataAgent, GeoAgent, etc.)
- **Fix optionnel**: `pip install camel-ai`

### 3. Latence élevée (~34s total)
- **Causes**:
  - Initialisation lazy des composants
  - Prompts trop verbeux
  - Pas de cache de résultats
- **Optimisations possibles**:
  - Pré-charger les composants au démarrage
  - Flash attention (`OLLAMA_FLASH_ATTENTION=1`)
  - Réduire les prompts système
  - Cache LRU pour requêtes similaires

## Améliorations prioritaires 📋

### P1 - Court terme
1. [ ] Configurer nomic-embed-text pour les embeddings
2. [ ] Ajouter `OLLAMA_FLASH_ATTENTION=1` au .env
3. [ ] Optimiser les prompts système (réduire tokens)

### P2 - Moyen terme
4. [ ] Pré-initialiser TAJINE au démarrage du backend
5. [ ] Ajouter cache LRU pour requêtes similaires
6. [ ] Implémenter le batch processing pour multi-requêtes

### P3 - Long terme
7. [ ] Fine-tuner un modèle spécialisé territorial
8. [ ] Ajouter un modèle plus puissant (qwen3:32b si la VRAM le permet)
9. [ ] Intégrer ROCm pour performance native AMD

## Configuration GPU optimale

```bash
# /etc/environment.d/ollama-gpu.conf
VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/radeon_icd.json
OLLAMA_VULKAN=1
OLLAMA_FLASH_ATTENTION=1
OLLAMA_NUM_PARALLEL=2
```

## Modèles installés

```
qwen3:14b          9.3 GB   Mode rapide (LOCAL tier)
qwen2.5:7b         4.7 GB   Backup / Vision
nomic-embed-text   274 MB   Embeddings
```

## VRAM Budget (24GB)

| Config | VRAM utilisée | Reste |
|--------|--------------|-------|
| qwen3:14b seul | ~10 GB | 14 GB |
| + nomic-embed | ~10.3 GB | 13.7 GB |
| + qwen3:32b | ~28 GB | ❌ Over |
| + qwen3:14b x2 | ~20 GB | 4 GB ✅ |

Conclusion: On peut charger 2 modèles 14B en parallèle, mais pas un 32B.
