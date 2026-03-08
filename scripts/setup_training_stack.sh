#!/bin/bash
# ============================================================================
# MPtoO Training Stack Setup
# Sets up LLaMA-Factory WebUI + Label Studio for fine-tuning workflow
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCKER_DIR="$PROJECT_ROOT/docker"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ============================================================================
# Check Prerequisites
# ============================================================================
check_gpu() {
    log_info "Checking GPU status..."

    if [ -e /dev/kfd ] && [ -e /dev/dri/renderD128 ]; then
        log_success "AMD GPU devices found"
        lspci -k | grep -A 2 "VGA.*AMD" | head -5
        return 0
    else
        log_error "AMD GPU devices not found"
        log_info "Make sure amdgpu driver is loaded: lsmod | grep amdgpu"
        return 1
    fi
}

check_docker() {
    log_info "Checking Docker..."

    if ! command -v docker &> /dev/null; then
        log_error "Docker not installed"
        return 1
    fi

    if ! docker info &> /dev/null; then
        log_error "Docker daemon not running"
        return 1
    fi

    log_success "Docker is running"
    return 0
}

# ============================================================================
# Setup Label Studio
# ============================================================================
setup_label_studio() {
    log_info "Setting up Label Studio..."

    if docker ps | grep -q label-studio; then
        log_success "Label Studio already running on http://localhost:8085"
        return 0
    fi

    cd "$DOCKER_DIR"
    docker-compose -f docker-compose.llama-factory.yml up -d label-studio

    log_info "Waiting for Label Studio to start..."
    sleep 10

    if curl -s http://localhost:8085 > /dev/null; then
        log_success "Label Studio running on http://localhost:8085"
    else
        log_warn "Label Studio may still be starting..."
    fi
}

# ============================================================================
# Setup LLaMA-Factory
# ============================================================================
setup_llama_factory() {
    log_info "Setting up LLaMA-Factory WebUI..."

    cd "$DOCKER_DIR"

    # Check if image exists
    if ! docker images | grep -q "mptoo-llama-factory"; then
        log_info "Building LLaMA-Factory image (this may take 10-15 minutes)..."
        docker-compose -f docker-compose.llama-factory.yml build llama-factory
    fi

    # Start container
    log_info "Starting LLaMA-Factory container..."
    docker-compose -f docker-compose.llama-factory.yml up -d llama-factory

    log_info "Waiting for LLaMA-Factory WebUI to start..."

    for i in {1..60}; do
        if curl -s http://localhost:7860 > /dev/null; then
            log_success "LLaMA-Factory WebUI running on http://localhost:7860"
            return 0
        fi
        sleep 2
    done

    log_warn "LLaMA-Factory may still be starting. Check with: docker logs llama-factory"
}

# ============================================================================
# Verify GPU in Container
# ============================================================================
verify_gpu_in_container() {
    log_info "Verifying GPU access in LLaMA-Factory container..."

    sleep 5

    docker exec llama-factory bash -c "
        echo '=== ROCm-SMI ===' && rocm-smi 2>/dev/null || echo 'rocm-smi not found'
        echo ''
        echo '=== PyTorch GPU ===' && python -c 'import torch; print(f\"CUDA available: {torch.cuda.is_available()}\"); print(f\"Device count: {torch.cuda.device_count()}\") if torch.cuda.is_available() else None' 2>/dev/null || echo 'PyTorch check failed'
    " 2>/dev/null || log_warn "Could not verify GPU in container"
}

# ============================================================================
# Print Summary
# ============================================================================
print_summary() {
    echo ""
    echo "============================================================================"
    echo -e "${GREEN}MPtoO Training Stack Ready!${NC}"
    echo "============================================================================"
    echo ""
    echo "Services:"
    echo "  - LLaMA-Factory WebUI:  http://localhost:7860"
    echo "  - Label Studio:         http://localhost:8085"
    echo "  - TensorBoard:          http://localhost:6006 (when training)"
    echo ""
    echo "Quick Start:"
    echo "  1. Open LLaMA-Factory WebUI at http://localhost:7860"
    echo "  2. Go to 'Train' tab"
    echo "  3. Select model: Qwen/Qwen2.5-Coder-7B-Instruct"
    echo "  4. Select dataset: mptoo_assistant"
    echo "  5. Configure LoRA parameters"
    echo "  6. Click 'Start'"
    echo ""
    echo "Label Studio (for data annotation):"
    echo "  1. Create account at http://localhost:8085"
    echo "  2. Create project for instruction tuning"
    echo "  3. Import your data from /root/MPtoO-V2/datasets"
    echo "  4. Export as JSONL after annotation"
    echo ""
    echo "Logs:"
    echo "  docker logs llama-factory -f"
    echo "  docker logs label-studio -f"
    echo ""
    echo "============================================================================"
}

# ============================================================================
# Main
# ============================================================================
main() {
    log_info "Starting MPtoO Training Stack Setup..."
    echo ""

    check_docker || exit 1
    check_gpu || log_warn "Continuing without GPU verification..."

    echo ""
    setup_label_studio

    echo ""
    setup_llama_factory

    echo ""
    verify_gpu_in_container

    print_summary
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
