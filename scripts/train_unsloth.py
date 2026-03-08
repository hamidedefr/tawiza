#!/usr/bin/env python3
"""
UAA Fine-Tuning Script using Unsloth
=====================================
Optimized for AMD RX 7900 XTX with ROCm

Usage:
    micromamba run -n training python scripts/train_unsloth.py \
        --dataset data/uaa_dataset.jsonl \
        --model qwen2.5-coder:7b \
        --output output/uaa_finetuned

Environment Variables:
    HSA_OVERRIDE_GFX_VERSION=11.0.0  (required for Navi 31)
    HIP_VISIBLE_DEVICES=0            (select GPU)
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Set AMD GPU compatibility
os.environ.setdefault("HSA_OVERRIDE_GFX_VERSION", "11.0.0")
os.environ.setdefault("HIP_VISIBLE_DEVICES", "0")


def check_gpu():
    """Verify GPU is accessible."""
    import torch

    print("=" * 60)
    print("GPU Check")
    print("=" * 60)
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA/ROCm available: {torch.cuda.is_available()}")

    if torch.cuda.is_available():
        print(f"GPU count: {torch.cuda.device_count()}")
        print(f"GPU name: {torch.cuda.get_device_name(0)}")
        print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        return True
    else:
        print("ERROR: No GPU detected!")
        print("Make sure:")
        print("  1. amdgpu driver is loaded (not vfio-pci)")
        print("  2. ROCm is installed: /opt/rocm/")
        print("  3. /dev/kfd exists")
        return False


def load_dataset(dataset_path: str):
    """Load dataset in JSONL format."""
    from datasets import Dataset

    examples = []
    with open(dataset_path) as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))

    print(f"Loaded {len(examples)} examples from {dataset_path}")
    return Dataset.from_list(examples)


def format_for_training(example):
    """Format example for instruction tuning."""
    instruction = example.get("instruction", "")
    input_text = example.get("input", "")
    output = example.get("output", "")

    if input_text:
        prompt = f"### Instruction:\n{instruction}\n\n### Input:\n{input_text}\n\n### Response:\n{output}"
    else:
        prompt = f"### Instruction:\n{instruction}\n\n### Response:\n{output}"

    return {"text": prompt}


def train(
    dataset_path: str,
    model_name: str = "unsloth/Qwen2.5-Coder-7B-Instruct",
    output_dir: str = "output/uaa_finetuned",
    epochs: int = 3,
    batch_size: int = 2,
    lora_r: int = 16,
    lora_alpha: int = 16,
    max_seq_length: int = 2048,
):
    """Run fine-tuning with Unsloth."""

    from transformers import TrainingArguments
    from trl import SFTTrainer
    from unsloth import FastLanguageModel

    print("\n" + "=" * 60)
    print("Loading Model")
    print("=" * 60)

    # Map Ollama model names to HuggingFace
    model_map = {
        "qwen2.5-coder:7b": "unsloth/Qwen2.5-Coder-7B-Instruct",
        "qwen2.5-coder:3b": "unsloth/Qwen2.5-Coder-3B-Instruct",
        "qwen2.5-coder:1.5b": "unsloth/Qwen2.5-Coder-1.5B-Instruct",
        "llama3.2:3b": "unsloth/Llama-3.2-3B-Instruct",
        "mistral:7b": "unsloth/mistral-7b-instruct-v0.3",
    }

    hf_model = model_map.get(model_name, model_name)
    print(f"Using model: {hf_model}")

    # Load with 4-bit quantization for memory efficiency
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=hf_model,
        max_seq_length=max_seq_length,
        load_in_4bit=True,
        dtype=None,  # Auto-detect
    )

    print(f"Model loaded with max_seq_length={max_seq_length}")

    # Apply LoRA
    print("\n" + "=" * 60)
    print("Applying LoRA")
    print("=" * 60)

    model = FastLanguageModel.get_peft_model(
        model,
        r=lora_r,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        lora_alpha=lora_alpha,
        lora_dropout=0,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=42,
    )

    print(f"LoRA applied: r={lora_r}, alpha={lora_alpha}")

    # Load dataset
    print("\n" + "=" * 60)
    print("Preparing Dataset")
    print("=" * 60)

    dataset = load_dataset(dataset_path)
    dataset = dataset.map(format_for_training)

    print(f"Dataset ready: {len(dataset)} examples")

    # Training arguments
    print("\n" + "=" * 60)
    print("Starting Training")
    print("=" * 60)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    training_args = TrainingArguments(
        output_dir=str(output_path),
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=4,
        warmup_steps=5,
        num_train_epochs=epochs,
        learning_rate=2e-4,
        fp16=True,
        logging_steps=1,
        save_strategy="epoch",
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="linear",
        seed=42,
        report_to="none",  # Disable wandb/mlflow
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=max_seq_length,
        args=training_args,
    )

    print(f"Training for {epochs} epochs with batch_size={batch_size}")

    # Train
    trainer.train()

    # Save
    print("\n" + "=" * 60)
    print("Saving Model")
    print("=" * 60)

    model.save_pretrained(str(output_path))
    tokenizer.save_pretrained(str(output_path))

    # Also save merged model for Ollama
    merged_path = output_path / "merged"
    model.save_pretrained_merged(str(merged_path), tokenizer, save_method="merged_16bit")

    print(f"Model saved to: {output_path}")
    print(f"Merged model at: {merged_path}")

    # Save training info
    info = {
        "timestamp": datetime.now().isoformat(),
        "base_model": hf_model,
        "dataset": dataset_path,
        "examples": len(dataset),
        "epochs": epochs,
        "lora_r": lora_r,
        "lora_alpha": lora_alpha,
    }

    with open(output_path / "training_info.json", "w") as f:
        json.dump(info, f, indent=2)

    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Create Ollama model:")
    print(f"   ollama create uaa-v1 -f {merged_path}/Modelfile")
    print("2. Test the model:")
    print("   ollama run uaa-v1")

    return str(output_path)


def main():
    parser = argparse.ArgumentParser(description="UAA Fine-Tuning with Unsloth")
    parser.add_argument("--dataset", type=str, required=True, help="Path to JSONL dataset")
    parser.add_argument(
        "--model",
        type=str,
        default="qwen2.5-coder:7b",
        help="Base model (Ollama name or HuggingFace ID)",
    )
    parser.add_argument(
        "--output", type=str, default="output/uaa_finetuned", help="Output directory"
    )
    parser.add_argument("--epochs", type=int, default=3, help="Training epochs")
    parser.add_argument("--batch-size", type=int, default=2, help="Batch size per device")
    parser.add_argument("--lora-r", type=int, default=16, help="LoRA rank")
    parser.add_argument("--lora-alpha", type=int, default=16, help="LoRA alpha")
    parser.add_argument("--max-seq-length", type=int, default=2048, help="Maximum sequence length")
    parser.add_argument("--check-gpu", action="store_true", help="Only check GPU and exit")

    args = parser.parse_args()

    if args.check_gpu:
        success = check_gpu()
        sys.exit(0 if success else 1)

    if not check_gpu():
        print("\nGPU not available. Cannot proceed with training.")
        sys.exit(1)

    train(
        dataset_path=args.dataset,
        model_name=args.model,
        output_dir=args.output,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lora_r=args.lora_r,
        lora_alpha=args.lora_alpha,
        max_seq_length=args.max_seq_length,
    )


if __name__ == "__main__":
    main()
