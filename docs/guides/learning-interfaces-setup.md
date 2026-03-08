# Interfaces d'Apprentissage UAA

Ce guide explique comment installer et utiliser les interfaces web pour l'annotation (Label Studio) et le fine-tuning (LLaMA-Factory).

## 1. Label Studio - Interface d'Annotation

### Installation avec Docker

```bash
# Démarrer Label Studio
docker run -d \
  --name label-studio \
  -p 8085:8080 \
  -v label-studio-data:/label-studio/data \
  -e LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true \
  heartexlabs/label-studio:latest

# Vérifier
docker logs -f label-studio
```

### Accès

- **URL**: http://localhost:8085
- Créer un compte au premier lancement
- Récupérer l'API key: Settings → Account → Access Token

### Configuration dans MPtoO

```bash
# Créer le fichier de config
cat > ~/.mptoo/label_studio.yaml << 'EOF'
label_studio:
  url: http://localhost:8085
  api_key: YOUR_API_KEY_HERE
  project_id: null  # Sera créé automatiquement
EOF
```

### Utilisation avec UAA

```bash
# 1. Pousser des candidats pour annotation
mptoo learning push --max 50

# 2. Annoter dans l'interface web (http://localhost:8085)
#    - Corriger les outputs si nécessaire
#    - Donner une note de qualité (1-5)

# 3. Récupérer les annotations
mptoo learning pull

# 4. Vérifier le statut
mptoo learning status
```

---

## 2. LLaMA-Factory - Interface de Fine-Tuning

### Installation

```bash
# Cloner LLaMA-Factory
cd /opt
git clone https://github.com/hiyouga/LLaMA-Factory.git
cd LLaMA-Factory

# Installer (AMD GPU avec ROCm)
pip install -e ".[torch,metrics]" --extra-index-url https://download.pytorch.org/whl/rocm6.0
```

### Lancer l'interface Web

```bash
cd /opt/LLaMA-Factory

# Interface WebUI (Gradio)
CUDA_VISIBLE_DEVICES=0 llamafactory-cli webui
# ou avec ROCm pour AMD GPU:
HIP_VISIBLE_DEVICES=0 llamafactory-cli webui
```

### Accès

- **URL**: http://localhost:7860
- Interface Gradio complète pour:
  - Sélection du modèle de base
  - Configuration LoRA/QLoRA/Full
  - Monitoring en temps réel
  - Évaluation et chat test

### Utilisation avec UAA

```bash
# 1. Exporter le dataset depuis UAA
mptoo learning export --output data/uaa_training.json --format alpaca

# 2. Dans l'interface LLaMA-Factory:
#    - Dataset: Sélectionner "alpaca" ou importer custom
#    - Model: qwen2.5-coder-7b (ou autre)
#    - Method: LoRA
#    - Cliquer "Start Training"

# 3. Après entraînement, le modèle sera dans:
#    /opt/LLaMA-Factory/saves/
```

---

## 3. Alternative: Unsloth (Plus rapide sur AMD)

```bash
# Installer Unsloth
pip install unsloth

# Script de fine-tuning rapide
python << 'EOF'
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Qwen2.5-Coder-7B-Instruct",
    max_seq_length=2048,
    load_in_4bit=True,
)

model = FastLanguageModel.get_peft_model(
    model,
    r=16,  # LoRA rank
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_alpha=16,
    lora_dropout=0,
)

# Charger dataset UAA
from datasets import load_dataset
dataset = load_dataset("json", data_files="data/uaa_training.json")

# Trainer...
EOF
```

---

## 4. Workflow Complet

```
┌────────────────────────────────────────────────────────────────┐
│                         WORKFLOW                               │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ÉTAPE 1: Collecte                                             │
│  ─────────────────                                             │
│  mptoo uaa execute "Tâche..."   # L'agent exécute              │
│  mptoo uaa feedback task positive/negative  # Feedback         │
│                                                                │
│  ÉTAPE 2: Annotation (Label Studio)                            │
│  ──────────────────────────────────                            │
│  mptoo learning push            # Envoie à Label Studio        │
│  → Ouvrir http://localhost:8085                                │
│  → Annoter, corriger, noter                                    │
│  mptoo learning pull            # Récupère annotations         │
│                                                                │
│  ÉTAPE 3: Fine-tuning (LLaMA-Factory)                          │
│  ────────────────────────────────────                          │
│  mptoo learning export          # Export dataset               │
│  → Ouvrir http://localhost:7860 (LLaMA-Factory WebUI)          │
│  → Configurer et lancer l'entraînement                         │
│                                                                │
│  ÉTAPE 4: Déploiement                                          │
│  ────────────────────                                          │
│  ollama create uaa-v1 -f Modelfile                             │
│  mptoo uaa config --set-model uaa-v1                           │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 5. Commandes Rapides

```bash
# Label Studio
docker start label-studio          # Démarrer
docker stop label-studio           # Arrêter
docker logs -f label-studio        # Logs

# LLaMA-Factory
cd /opt/LLaMA-Factory && llamafactory-cli webui  # Interface

# UAA Learning Pipeline
mptoo learning status              # Statut
mptoo learning push                # → Label Studio
mptoo learning pull                # ← Label Studio
mptoo learning train               # Fine-tune direct
mptoo learning export              # Export dataset
mptoo learning full-cycle          # Tout automatique
```

## 6. Configuration AMD GPU (RX 7900 XTX)

```bash
# Vérifier ROCm
rocm-smi

# Variables d'environnement
export HIP_VISIBLE_DEVICES=0
export HSA_OVERRIDE_GFX_VERSION=11.0.0  # Pour Navi 31

# PyTorch ROCm
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.0
```
