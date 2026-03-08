"""Gestion des agents - Configuration et monitoring."""

import streamlit as st

st.set_page_config(page_title="Agents", page_icon="🤖", layout="wide")

st.title("🤖 Gestion des Agents")

# Agent selection
agent_type = st.selectbox(
    "Sélectionner un agent", ["Cadreur", "Collecteur", "Analyste", "Rédacteur"]
)

st.divider()

# Agent configuration
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"⚙️ Configuration - {agent_type}")

    if agent_type == "Cadreur":
        model = st.selectbox("Modèle LLM", ["qwen3-coder:30b", "llama3.1:8b"])
        timeout = st.slider("Timeout (s)", 30, 300, 120)
        max_tokens = st.number_input("Max tokens", 512, 8192, 4096)

    elif agent_type == "Collecteur":
        st.multiselect(
            "Sources activées",
            ["sirene", "bodacc", "datasubvention", "aides_territoires"],
            default=["sirene", "bodacc"],
        )
        parallel = st.checkbox("Collecte parallèle", value=True)
        rate_limit = st.number_input("Rate limit (req/min)", 10, 100, 30)

    elif agent_type == "Analyste":
        model = st.selectbox("Modèle LLM", ["qwen3-coder:30b", "llama3.1:8b"])
        sandbox = st.checkbox("Sandbox OpenManus", value=False)
        charts = st.checkbox("Génération graphiques", value=True)

    elif agent_type == "Rédacteur":
        model = st.selectbox("Modèle LLM", ["ministral-3:14b", "qwen3-coder:30b"])
        style = st.selectbox("Style rapport", ["Professionnel", "Académique", "Synthétique"])
        max_pages = st.slider("Pages max", 5, 50, 20)

    if st.button("💾 Sauvegarder", type="primary"):
        st.success("Configuration sauvegardée !")

with col2:
    st.subheader("📊 Métriques")

    # Demo metrics
    st.metric("Appels aujourd'hui", 42, delta="+5")
    st.metric("Temps moyen", "3.2s", delta="-0.3s")
    st.metric("Taux succès", "98.5%", delta="+1.2%")

    st.subheader("📋 Logs récents")
    st.code("""
[2024-12-08 10:45:23] INFO - Cadreur: Frame created
[2024-12-08 10:45:21] INFO - Cadreur: Framing question...
[2024-12-08 10:43:12] INFO - Cadreur: Agent initialized
    """)
