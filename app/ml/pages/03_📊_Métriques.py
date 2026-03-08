"""Métriques - Évaluation des modèles."""

import streamlit as st

st.set_page_config(page_title="Métriques", page_icon="📊", layout="wide")

st.title("📊 Métriques des Modèles")

# Model selection
model = st.selectbox(
    "Sélectionner un modèle", ["mptoo-assistant", "qwen3-coder:30b", "ministral-3:14b"]
)

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 Métriques de qualité")

    metrics = {
        "BLEU": 0.72,
        "ROUGE-L": 0.78,
        "Exact Match": 0.65,
        "F1 Score": 0.81,
    }

    for name, value in metrics.items():
        st.metric(name, f"{value:.2%}")

with col2:
    st.subheader("⚡ Performance")

    perf = {
        "Latence moyenne": "2.3s",
        "Tokens/seconde": "45.2",
        "Mémoire GPU": "18.5 GB",
        "Throughput": "12 req/min",
    }

    for name, value in perf.items():
        st.metric(name, value)

st.divider()

st.subheader("📈 Historique d'évaluation")

st.line_chart(
    {
        "BLEU": [0.65, 0.68, 0.70, 0.72, 0.72],
        "ROUGE-L": [0.70, 0.73, 0.75, 0.77, 0.78],
    }
)

st.subheader("🧪 Lancer une évaluation")

benchmark = st.selectbox("Benchmark", ["MPtoO QA", "Territorial Eval", "Custom"])

if st.button("▶️ Exécuter"):
    with st.spinner("Évaluation en cours..."):
        st.success("Évaluation terminée !")
