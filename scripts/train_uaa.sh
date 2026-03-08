#!/bin/bash
# UAA Training Script with Unsloth
# Wrapper for easy training execution

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}   UAA Fine-Tuning with Unsloth        ${NC}"
echo -e "${CYAN}   AMD RX 7900 XTX (ROCm)              ${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Check environment
if ! command -v micromamba &> /dev/null; then
    echo -e "${RED}Error: micromamba not found${NC}"
    echo "Install with: curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj bin/micromamba"
    exit 1
fi

# Check if training environment exists
if ! micromamba env list | grep -q "training"; then
    echo -e "${YELLOW}Creating training environment...${NC}"
    micromamba create -n training python=3.11 -c conda-forge -y
    micromamba run -n training pip install torch torchvision --index-url https://download.pytorch.org/whl/rocm6.4
    micromamba run -n training pip install unsloth transformers datasets accelerate peft trl
fi

# Set AMD GPU environment
export HSA_OVERRIDE_GFX_VERSION=11.0.0
export HIP_VISIBLE_DEVICES=0

# Default paths
DATASET="${1:-data/uaa_dataset.jsonl}"
OUTPUT="${2:-output/uaa_finetuned}"

# Check dataset
if [ ! -f "$DATASET" ]; then
    echo -e "${YELLOW}No dataset found at $DATASET${NC}"
    echo ""
    echo "Export UAA dataset first:"
    echo -e "  ${CYAN}mptoo learning export --output $DATASET${NC}"
    echo ""
    echo "Or specify a different path:"
    echo -e "  ${CYAN}$0 /path/to/dataset.jsonl${NC}"
    exit 1
fi

# Count examples
EXAMPLES=$(wc -l < "$DATASET")
echo -e "${GREEN}Dataset: $DATASET ($EXAMPLES examples)${NC}"
echo -e "${GREEN}Output:  $OUTPUT${NC}"
echo ""

# Check GPU
echo -e "${YELLOW}Checking GPU...${NC}"
micromamba run -n training python /root/MPtoO-V2/scripts/train_unsloth.py --check-gpu

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}GPU check failed!${NC}"
    echo ""
    echo "Make sure:"
    echo "  1. System was rebooted after GPU config change"
    echo "  2. amdgpu driver is loaded: lsmod | grep amdgpu"
    echo "  3. /dev/kfd exists: ls -la /dev/kfd"
    echo ""
    echo "If GPU is still on vfio-pci, run:"
    echo "  echo '0000:07:00.0' | sudo tee /sys/bus/pci/drivers/vfio-pci/unbind"
    echo "  sudo modprobe amdgpu"
    exit 1
fi

echo ""
echo -e "${GREEN}GPU OK! Starting training...${NC}"
echo ""

# Run training
micromamba run -n training python /root/MPtoO-V2/scripts/train_unsloth.py \
    --dataset "$DATASET" \
    --output "$OUTPUT" \
    --model qwen2.5-coder:7b \
    --epochs 3 \
    --batch-size 2 \
    --lora-r 16

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Training Complete!                  ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Model saved to: $OUTPUT"
echo ""
echo "Next steps:"
echo -e "  1. Create Ollama model: ${CYAN}ollama create uaa-v1 -f $OUTPUT/merged/Modelfile${NC}"
echo -e "  2. Test: ${CYAN}ollama run uaa-v1${NC}"
echo -e "  3. Configure UAA: ${CYAN}mptoo uaa config --set-model uaa-v1${NC}"
