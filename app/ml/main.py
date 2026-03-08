"""MPtoO ML Platform - Fine-tuning et métriques."""

import streamlit as st

st.set_page_config(
    page_title="MPtoO ML", page_icon="🧠", layout="wide", initial_sidebar_state="expanded"
)

st.title("🧠 MPtoO - ML Platform")

st.markdown("""
## Plateforme Machine Learning

Gérez le fine-tuning et les métriques de vos modèles.

### Fonctionnalités

- 🏋️ **Fine-Tuning** - Entraînement LoRA avec LLaMA-Factory
- 📦 **Datasets** - Gestion des jeux de données
- 📊 **Métriques** - BLEU, ROUGE-L, latence
- 🏷️ **Annotations** - Intégration Label Studio
""")

with st.sidebar:
    st.header("🔬 ML Config")
    st.info("ML Platform v2.0")
    st.metric("GPU", "RX 7900 XTX", delta="24GB VRAM")
