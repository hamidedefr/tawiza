#!/bin/bash
# Script de fine-tuning MPtoO Assistant avec Docker ROCm
# Utilise LLaMA-Factory pour fine-tuner Qwen Coder

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DOCKER_DIR="$PROJECT_DIR/docker"

echo "=========================================="
echo " MPtoO Assistant Fine-Tuning (ROCm)"
echo "=========================================="
echo ""

# 1. Vérification GPU
echo "[1/5] Vérification du GPU AMD..."
if [ ! -e /dev/kfd ]; then
    echo "ERREUR: /dev/kfd non trouvé!"
    echo "Le GPU AMD n'est pas accessible. Vérifiez:"
    echo "  - Driver amdgpu chargé: lsmod | grep amdgpu"
    echo "  - lspci -k | grep -A 3 'VGA.*AMD'"
    exit 1
fi

if [ ! -e /dev/dri/renderD128 ]; then
    echo "ERREUR: /dev/dri/renderD128 non trouvé!"
    exit 1
fi

echo "  /dev/kfd        : OK"
echo "  /dev/dri/render : OK"
echo ""

# 2. Vérification Docker
echo "[2/5] Vérification Docker..."
if ! command -v docker &> /dev/null; then
    echo "ERREUR: Docker non installé"
    exit 1
fi
if ! docker info &> /dev/null; then
    echo "ERREUR: Docker daemon non accessible"
    exit 1
fi
echo "  Docker          : OK"
echo ""

# 3. Vérification des fichiers
echo "[3/5] Vérification des fichiers..."
if [ ! -f "$PROJECT_DIR/datasets/mptoo_assistant_train.jsonl" ]; then
    echo "ERREUR: Dataset non trouvé: $PROJECT_DIR/datasets/mptoo_assistant_train.jsonl"
    exit 1
fi
if [ ! -f "$PROJECT_DIR/configs/finetune_mptoo_assistant_qwen_amd.yaml" ]; then
    echo "ERREUR: Config non trouvé: $PROJECT_DIR/configs/finetune_mptoo_assistant_qwen_amd.yaml"
    exit 1
fi
echo "  Dataset         : OK"
echo "  Config          : OK"
echo ""

# 4. Build de l'image Docker
echo "[4/5] Construction de l'image Docker ROCm..."
echo "  (Cela peut prendre 5-10 minutes la première fois)"
cd "$DOCKER_DIR"
docker compose -f docker-compose.rocm-training.yml build

echo ""
echo "[5/5] Démarrage du conteneur..."

# Créer le répertoire de logs
mkdir -p "$DOCKER_DIR/training_logs"

# Démarrer le conteneur
docker compose -f docker-compose.rocm-training.yml up -d

echo ""
echo "=========================================="
echo " Conteneur démarré!"
echo "=========================================="
echo ""
echo "Vérification GPU dans le conteneur..."
sleep 3
docker exec mptoo-training-rocm rocm-smi || echo "rocm-smi non disponible, vérifie PyTorch..."
echo ""

echo "Test PyTorch + GPU..."
docker exec mptoo-training-rocm python -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'ROCm available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}')
    print(f'VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')
"

echo ""
echo "=========================================="
echo " Lancement du fine-tuning"
echo "=========================================="
echo ""

# Lancer le training
docker exec -it mptoo-training-rocm bash -c "
cd /workspace
echo 'Vérification LLaMA-Factory...'
llamafactory-cli version || pip install llamafactory

echo ''
echo 'Démarrage du fine-tuning Qwen Coder...'
echo ''

llamafactory-cli train configs/finetune_mptoo_assistant_qwen_amd.yaml
"

echo ""
echo "=========================================="
echo " Fine-tuning terminé!"
echo "=========================================="
echo ""
echo "Le modèle est sauvegardé dans: $PROJECT_DIR/output/mptoo_assistant_qwen_lora"
echo ""
echo "Pour exporter vers Ollama:"
echo "  docker exec -it mptoo-training-rocm llamafactory-cli export \\"
echo "    --model_name_or_path Qwen/Qwen2.5-Coder-7B-Instruct \\"
echo "    --adapter_name_or_path /workspace/output/mptoo_assistant_qwen_lora \\"
echo "    --template qwen \\"
echo "    --finetuning_type lora \\"
echo "    --export_dir /workspace/output/mptoo_assistant_merged \\"
echo "    --export_size 4 \\"
echo "    --export_quantization_bit 4"
