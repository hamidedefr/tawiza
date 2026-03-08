"""Fine-tuning - Entraînement LoRA avec interface vers LLaMA-Factory."""

import json
import os
from pathlib import Path

import httpx
import streamlit as st

st.set_page_config(page_title="Fine-Tuning", page_icon="🏋️", layout="wide")

st.title("🏋️ Fine-Tuning")

# Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
LLAMA_FACTORY_URL = os.getenv("LLAMA_FACTORY_URL", "http://localhost:7860")
DATASETS_PATH = "/app/datasets"

# Check LLaMA-Factory availability
llama_factory_status = "🔴 Inactif"
try:
    r = httpx.get(LLAMA_FACTORY_URL, timeout=5)
    if r.status_code == 200:
        llama_factory_status = "🟢 Actif"
except Exception:
    pass

st.info(f"LLaMA-Factory WebUI: {llama_factory_status} - {LLAMA_FACTORY_URL}")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📦 Configuration")

    # Get available models from Ollama - REAL data
    available_models = []
    try:
        r = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=10)
        if r.status_code == 200:
            models = r.json().get("models", [])
            available_models = [m["name"] for m in models]
    except Exception:
        available_models = ["qwen3-coder:30b", "llama3.1:8b", "mistral:7b"]

    base_model = st.selectbox(
        "Modèle de base", available_models if available_models else ["Aucun modèle disponible"]
    )

    # List real datasets
    dataset_options = []
    datasets_info = {}

    # Check for real dataset files
    common_dataset_paths = [
        "/app/datasets",
        "/root/MPtoO-V2/datasets",
    ]

    for dataset_path in common_dataset_paths:
        p = Path(dataset_path)
        if p.exists():
            for f in p.glob("*.jsonl"):
                name = f.stem
                try:
                    with open(f) as fp:
                        lines = fp.readlines()
                        count = len(lines)
                        datasets_info[name] = {"path": str(f), "count": count}
                        dataset_options.append(name)
                except Exception:
                    pass

    if not dataset_options:
        dataset_options = ["mptoo_assistant_train", "evaluation_qa"]
        datasets_info = {
            "mptoo_assistant_train": {"path": "N/A", "count": 22},
            "evaluation_qa": {"path": "N/A", "count": 0},
        }

    dataset = st.selectbox("Dataset", dataset_options)

    if dataset in datasets_info:
        st.caption(
            f"📄 {datasets_info[dataset]['count']} exemples - {datasets_info[dataset]['path']}"
        )

    st.markdown("**Hyperparamètres LoRA**")
    epochs = st.slider("Époques", 1, 10, 3)
    batch_size = st.selectbox("Batch size", [1, 2, 4, 8], index=1)
    learning_rate = st.select_slider(
        "Learning rate",
        options=[1e-5, 2e-5, 5e-5, 1e-4, 2e-4],
        value=2e-5,
        format_func=lambda x: f"{x:.0e}",
    )
    lora_rank = st.selectbox("LoRA rank", [8, 16, 32, 64], index=1)
    lora_alpha = st.selectbox("LoRA alpha", [16, 32, 64, 128], index=1)

    # Generate LLaMA-Factory config
    if st.button("📋 Générer la config", type="secondary"):
        config = {
            "model_name_or_path": base_model.split(":")[0],
            "dataset": dataset,
            "finetuning_type": "lora",
            "lora_rank": lora_rank,
            "lora_alpha": lora_alpha,
            "lora_target": "all",
            "num_train_epochs": epochs,
            "per_device_train_batch_size": batch_size,
            "learning_rate": learning_rate,
            "output_dir": f"./saves/{dataset}_{base_model.replace(':', '_')}",
        }
        st.code(json.dumps(config, indent=2), language="json")
        st.download_button(
            "💾 Télécharger config.json",
            json.dumps(config, indent=2),
            file_name=f"lora_config_{dataset}.json",
            mime="application/json",
        )

    if st.button("🚀 Ouvrir LLaMA-Factory", type="primary"):
        st.markdown(
            f"""
        <a href="{LLAMA_FACTORY_URL}" target="_blank" style="
            display: inline-block;
            padding: 0.5rem 1rem;
            background-color: #FF4B4B;
            color: white;
            text-decoration: none;
            border-radius: 0.5rem;
        ">Ouvrir LLaMA-Factory WebUI →</a>
        """,
            unsafe_allow_html=True,
        )

with col2:
    st.subheader("📊 Modèles Fine-tunés")

    # Check for fine-tuned models in Ollama
    finetuned_models = [m for m in available_models if "mptoo" in m.lower() or "ft-" in m.lower()]

    if finetuned_models:
        for model in finetuned_models:
            with st.expander(f"✅ {model}"):
                st.write("Modèle fine-tuné disponible")
                if st.button(f"🧪 Tester {model}", key=f"test_{model}"):
                    test_prompt = st.text_input(
                        "Prompt de test", value="Qu'est-ce que MPtoO ?", key=f"prompt_{model}"
                    )
                    if test_prompt:
                        try:
                            with st.spinner("Génération..."):
                                r = httpx.post(
                                    f"{OLLAMA_URL}/api/generate",
                                    json={"model": model, "prompt": test_prompt, "stream": False},
                                    timeout=60,
                                )
                                if r.status_code == 200:
                                    response = r.json().get("response", "")
                                    st.success("Réponse:")
                                    st.write(response)
                        except Exception as e:
                            st.error(f"Erreur: {e}")
    else:
        st.info(
            "Aucun modèle fine-tuné trouvé. Les modèles contenant 'mptoo' ou 'ft-' seront listés ici."
        )

    st.subheader("📈 Ressources GPU")

    # Show GPU info if available
    try:
        import subprocess

        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.used,memory.total,utilization.gpu",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            for line in lines:
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 4:
                    st.metric(parts[0], f"{parts[3]}% GPU", delta=f"{parts[1]}/{parts[2]} MB")
        else:
            st.info("GPU NVIDIA non détecté dans le conteneur")
    except Exception:
        st.info("Vérification GPU non disponible (ROCm/CPU)")

    # Training tips
    st.subheader("💡 Conseils")
    st.markdown("""
    - **Batch size 1-2**: Pour GPU < 24GB VRAM
    - **LoRA rank 16-32**: Bon équilibre performance/mémoire
    - **3-5 époques**: Suffisant pour fine-tuning léger
    - **Learning rate 2e-5**: Point de départ recommandé
    """)
