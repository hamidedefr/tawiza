# MPtoO CLI Documentation

Guide complet pour utiliser la CLI MPtoO avec tous les agents et commandes.

## Table des matières

1. [Installation et Configuration](#installation-et-configuration)
2. [Commandes de Base](#commandes-de-base)
3. [Agents AI](#agents-ai)
4. [Analyse Territoriale](#analyse-territoriale)
5. [Gestion des Modèles](#gestion-des-modèles)
6. [GPU et Performance](#gpu-et-performance)
7. [Configuration](#configuration)
8. [API REST](#api-rest)
9. [Troubleshooting](#troubleshooting)

---

## Installation et Configuration

### Prérequis

```bash
# Ollama doit être installé et accessible
curl http://localhost:11434/api/tags

# Variables d'environnement importantes
export OLLAMA_URL=http://localhost:11434
```

### Fichier .env

```bash
# /root/MPtoO-V2/.env
OLLAMA_URL=http://localhost:11434
OLLAMA_BASE_URL=http://localhost:11434
```

### Vérification de l'installation

```bash
# Vérifier le statut du système
mptoo status

# Diagnostics complets
mptoo pro doctor

# Informations système
mptoo pro info
```

---

## Commandes de Base

### Statut et Dashboard

```bash
# Statut rapide
mptoo status

# Dashboard interactif TUI
mptoo tui

# Dashboard pro avec métriques
mptoo pro dashboard

# Services actifs
mptoo pro services

# Liens rapides
mptoo pro links
```

### Chat

```bash
# Chat interactif avec l'assistant
mptoo chat

# Chat avec un modèle spécifique
mptoo chat --model qwen3-coder:30b
```

---

## Agents AI

### Liste des Agents

```bash
# Liste simple
mptoo pro agent-list

# Liste détaillée avec statut
mptoo pro agents

# Capacités d'un agent
mptoo pro agent-capabilities manus
```

### Agents Disponibles

| Agent | Description | Cas d'usage |
|-------|-------------|-------------|
| `manus` | Agent de raisonnement avec boucle think-execute | Recherche, analyse, tâches complexes |
| `s3` | Automatisation browser + desktop | Web scraping, interactions UI |
| `analyst` | Analyse de données | Insights, rapports |
| `coder` | Génération de code | Code review, développement |
| `browser` | Automatisation web | Scraping, tests |
| `ml` | Machine Learning | Entraînement, prédictions |
| `research` | Recherche approfondie multi-sources | Veille, documentation |
| `crawler` | Web crawling | Extraction de contenu |

### Exécuter un Agent

```bash
# Syntaxe générale
mptoo pro agent-run <agent> -t "<tâche>" [options]

# Options disponibles
#   -t, --task      Tâche à exécuter (requis)
#   -m, --model     Modèle LLM (défaut: qwen3:14b)
#   --max-iter      Itérations max (défaut: 10)
#   -v, --verbose   Sortie détaillée
#   -o, --output    Sauvegarder le résultat
#   --mode          Mode agent (browser/desktop/hybrid)
```

### Exemples par Agent

#### Manus - Agent de Raisonnement

```bash
# Recherche web avec synthèse
mptoo pro agent-run manus \
  -t "Recherche les dernières nouvelles sur Ollama et liste les nouveaux modèles disponibles" \
  --model qwen3:14b \
  -v \
  --max-iter 5

# Analyse d'un sujet technique
mptoo pro agent-run manus \
  -t "Explique les différences entre LLaMA 3.3 et Qwen 3" \
  --model qwen3-coder:30b \
  -v

# Tâche complexe multi-étapes
mptoo pro agent-run manus \
  -t "Compare les frameworks AI open source (Ollama, LM Studio, GPT4All) et crée un tableau comparatif" \
  --max-iter 10 \
  -o comparison.json
```

#### S3 - Automatisation Browser/Desktop

```bash
# Mode browser (scraping web)
mptoo pro agent-run s3 \
  -t "Navigue sur github.com/ollama/ollama et liste les dernières releases" \
  --mode browser \
  -v

# Mode desktop (automatisation UI)
mptoo pro agent-run s3 \
  -t "Ouvre le terminal et exécute 'ollama list'" \
  --mode desktop \
  -v

# Mode hybride
mptoo pro agent-run s3 \
  -t "Télécharge la page d'accueil d'Ollama et sauvegarde en PDF" \
  --mode hybrid \
  -v
```

#### Research - Recherche Approfondie

```bash
# Recherche simple
mptoo pro agent-run research \
  -t "État de l'art des LLM open source en 2024" \
  -v

# Recherche avec profondeur
mptoo pro agent-run research \
  -t "Nouvelles tendances en IA générative" \
  --max-iter 15 \
  -o research_output.json
```

#### Analyst - Analyse de Données

```bash
# Analyse d'un dataset
mptoo pro agent-run analyst \
  -t "Analyse le fichier data.csv et génère des insights" \
  -v

# Statistiques descriptives
mptoo pro agent-run analyst \
  -t "Calcule les statistiques clés pour le dataset sales_2024.csv" \
  -o stats.json
```

#### Coder - Génération de Code

```bash
# Génération de code
mptoo pro agent-run coder \
  -t "Crée une fonction Python qui parse un fichier JSON et retourne un DataFrame pandas" \
  --model qwen3-coder:30b \
  -v

# Code review
mptoo pro agent-run coder \
  -t "Review le fichier main.py et suggère des améliorations" \
  -v
```

#### Crawler - Web Crawling

```bash
# Crawl d'un site
mptoo pro agent-run crawler \
  -t "Crawle https://ollama.com/blog et extrait tous les articles" \
  -v

# Extraction ciblée
mptoo pro agent-run crawler \
  -t "Extrait les prix des produits de https://example.com/products" \
  -o products.json
```

### Debug des Agents

```bash
# Mode debug détaillé
mptoo pro agent-debug manus \
  -t "Test simple" \
  -v

# Voir les logs en temps réel
mptoo pro logs-show --follow
```

---

## Analyse Territoriale

L'analyse territoriale utilise le système multi-agent Camel AI pour analyser des marchés.

### Niveaux de Profondeur

| Niveau | Description | Temps |
|--------|-------------|-------|
| `quick` | Recherche Sirene + rapport basique | ~10s |
| `standard` | + Carte + export CSV | ~30s |
| `full` | + Enrichissement web + graphe | 2-5min |

### Exemples

```bash
# Analyse rapide
mptoo analyze "conseil IT Lille"

# Analyse standard avec verbosité
mptoo analyze "startups IA Hauts-de-France" --depth standard -v

# Analyse complète
mptoo analyze "agences web Paris" --depth full -v

# Avec multi-agents Camel AI
mptoo analyze "startups IA Lille" --use-agents -v

# Multi-source (8 sources en parallèle)
mptoo analyze "conseil digital Lyon" --multi-source -v

# Mode interactif (questions de suivi)
mptoo analyze "cabinet conseil RH Bordeaux" --interactive

# Avec limite d'entreprises
mptoo analyze "restaurants Marseille" --limit 50 --depth full

# Export dans un dossier spécifique
mptoo analyze "freelances développement Nantes" -o ./exports/nantes/
```

---

## Gestion des Modèles

### Lister les Modèles

```bash
# Modèles locaux (Proxmox)
mptoo pro model-list

# Modèles sur VM GPU
curl http://localhost:11434/api/tags | jq '.models[].name'
```

### Télécharger un Modèle

```bash
# Pull un modèle
mptoo pro model-pull qwen3:14b

# Pull directement via curl (VM GPU)
curl http://localhost:11434/api/pull -d '{"name": "llama3.3:70b"}'
```

### Modèles Recommandés

| Modèle | Taille | Usage |
|--------|--------|-------|
| `qwen3:14b` | 9GB | Usage général, rapide |
| `qwen3-coder:30b` | 18GB | Code, raisonnement |
| `llama3.3:70b` | 40GB | Tâches complexes |
| `nomic-embed-text` | 270MB | Embeddings |
| `llava:13b` | 8GB | Vision/images |

---

## GPU et Performance

### Statut GPU

```bash
# Statut basique
mptoo pro gpu-status

# Informations complètes
mptoo pro gpu-info

# Monitoring temps réel
mptoo pro gpu-monitor

# Benchmark
mptoo pro gpu-benchmark
```

### GPU Passthrough (VMs)

```bash
# Statut du passthrough
mptoo pro gpu-passthrough-status

# Activer passthrough
mptoo pro gpu-passthrough-enable

# Désactiver passthrough
mptoo pro gpu-passthrough-disable

# VMs avec GPU
mptoo pro gpu-vm-list
```

### Métriques

```bash
# Métriques système
mptoo pro metrics

# Métriques live
mptoo pro metrics-live

# Historique
mptoo pro metrics-history

# Enregistrer métriques
mptoo pro metrics-record
```

---

## Configuration

### Voir la Configuration

```bash
# Configuration actuelle
mptoo pro config-show

# Chemins des fichiers
mptoo pro config-path
```

### Modifier la Configuration

```bash
# Définir une valeur
mptoo pro config-set ollama.url http://localhost:11434

# Éditeur interactif
mptoo pro config-edit

# Reset aux valeurs par défaut
mptoo pro config-reset
```

### Cache

```bash
# Informations cache
mptoo pro cache-info

# Vider le cache
mptoo pro cache-clear
```

### Logs

```bash
# Voir les logs
mptoo pro logs-show

# Logs en temps réel
mptoo pro logs-show --follow

# Effacer les logs
mptoo pro logs-clear
```

---

## API REST

L'API REST est accessible sur le port 8000.

### Démarrer l'API

```bash
cd /root/MPtoO-V2
.venv/bin/uvicorn src.interfaces.api.main:app --host 0.0.0.0 --port 8000
```

### Endpoints Principaux

```bash
# Health check
curl http://localhost:8000/health

# Liste des agents
curl http://localhost:8000/api/v1/agents/health

# OpenAI-compatible
curl http://localhost:8000/v1/models
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen3:14b", "messages": [{"role": "user", "content": "Hello"}]}'
```

### Documentation API

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Troubleshooting

### Problèmes Courants

#### Ollama non accessible

```bash
# Vérifier la connectivité
curl http://localhost:11434/api/tags

# Vérifier la variable d'environnement
echo $OLLAMA_URL

# S'assurer que le fichier .env est correct
cat /root/MPtoO-V2/.env | grep OLLAMA
```

#### Agent timeout

```bash
# Augmenter les itérations
mptoo pro agent-run manus -t "..." --max-iter 20

# Utiliser un modèle plus petit
mptoo pro agent-run manus -t "..." --model qwen3:14b
```

#### S3/MinIO non disponible

C'est normal si MinIO n'est pas démarré. L'agent fonctionne sans cache S3.

```bash
# Vérifier les logs pour confirmation
# "⚠️ S3 connection failed (caching disabled)" = OK, continue sans cache
```

#### Qdrant vector dimension mismatch

```bash
# S'assurer que nomic-embed-text est installé
curl http://localhost:11434/api/pull -d '{"name": "nomic-embed-text"}'
```

### Diagnostics

```bash
# Diagnostic complet
mptoo pro doctor

# Vérifier les sources de données
mptoo sources status
mptoo sources test

# Synchroniser les sources
mptoo sources sync
```

### Logs et Debug

```bash
# Logs en temps réel
mptoo pro logs-show --follow

# Debug d'un agent
mptoo pro agent-debug manus -t "test" -v

# Export métriques pour analyse
mptoo pro metrics-export
```

---

## Exemples Complets

### Scénario 1: Veille Technologique

```bash
# Recherche sur un sujet tech
mptoo pro agent-run manus \
  -t "Quelles sont les dernières avancées en LLM open source (décembre 2024)? Liste les nouveaux modèles et leurs caractéristiques." \
  --model qwen3-coder:30b \
  --max-iter 10 \
  -v \
  -o veille_llm_2024.json
```

### Scénario 2: Analyse de Marché

```bash
# Analyse territoriale complète
mptoo analyze "agences marketing digital Lille" \
  --depth full \
  --use-agents \
  --limit 30 \
  -v \
  -o ./analyses/marketing_lille/
```

### Scénario 3: Automatisation Web

```bash
# Scraping avec l'agent S3
mptoo pro agent-run s3 \
  -t "Visite https://news.ycombinator.com et extrait les 10 premiers titres" \
  --mode browser \
  -v
```

### Scénario 4: Génération de Code

```bash
# Créer un script
mptoo pro agent-run coder \
  -t "Crée un script Python qui lit un fichier CSV, calcule les moyennes par colonne, et exporte en JSON" \
  --model qwen3-coder:30b \
  -v \
  -o script.py
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     MPtoO CLI (mptoo)                       │
├─────────────────────────────────────────────────────────────┤
│  pro commands │ analyze │ sources │ chat │ status │ tui    │
├───────────────┴─────────┴─────────┴──────┴────────┴────────┤
│                    Agent Registry                           │
│  ┌─────────┬─────────┬──────────┬─────────┬──────────────┐ │
│  │  Manus  │   S3    │ Analyst  │  Coder  │   Research   │ │
│  └─────────┴─────────┴──────────┴─────────┴──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│              Infrastructure Layer                           │
│  ┌─────────────┬──────────────┬───────────────────────┐    │
│  │   Ollama    │    Qdrant    │   DeepResearchAgent   │    │
│  │  (VM 400)   │   (Vector)   │   (Web + LLM)         │    │
│  └─────────────┴──────────────┴───────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## Raccourcis Utiles

```bash
# Alias recommandés (ajouter à ~/.bashrc)
alias mp='mptoo'
alias mpa='mptoo pro agents'
alias mpr='mptoo pro agent-run'
alias mps='mptoo status'
alias mpd='mptoo pro dashboard'

# Exemples avec alias
mpr manus -t "Recherche XYZ" -v
mpa  # Liste des agents
```

---

*Documentation générée le 2024-12-10*
*Version: MPtoO-V2*
