"""Page d'évaluation - Saisie de question et suivi de l'analyse."""

import asyncio
import os
from datetime import datetime

import streamlit as st

# Import du workflow local (autonome, sans dépendances complexes)
from app.evaluator.agents import EvaluationWorkflow, WorkflowResult, WorkflowStatus

# Configuration de la page
st.set_page_config(page_title="Évaluation", page_icon="📊", layout="wide")

st.title("📊 Nouvelle Évaluation")

# Afficher la configuration Ollama
ollama_url = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")
with st.expander("⚙️ Configuration", expanded=False):
    st.code(f"Ollama URL: {ollama_url}")
    st.code(f"Modèle: {os.getenv('LLM_MODEL', 'qwen2.5:14b')}")

# Session state initialization
if "evaluation_result" not in st.session_state:
    st.session_state.evaluation_result = None
if "evaluation_status" not in st.session_state:
    st.session_state.evaluation_status = None

# Mode selection
mode = st.radio(
    "Mode d'analyse",
    ["🎯 Simple", "🔧 Expert"],
    horizontal=True,
    help="Le mode Expert permet de configurer les sources et paramètres",
)

# Question input
st.subheader("Votre question d'évaluation")
question = st.text_area(
    "Décrivez la problématique à évaluer",
    placeholder="Exemple: Quel est l'impact des incubateurs France 2030 sur l'emploi dans les Hauts-de-France ?",
    height=100,
)

# Expert mode options
if mode == "🔧 Expert":
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Territoire**")
        territory = st.selectbox(
            "Région d'analyse",
            ["hauts-de-france", "ile-de-france", "auvergne-rhone-alpes", "occitanie"],
        )

        st.markdown("**Période**")
        period_start = st.selectbox("Année de début", list(range(2015, 2025)), index=5)
        period_end = st.selectbox("Année de fin", list(range(2020, 2026)), index=4)

    with col2:
        st.markdown("**Sources de données**")
        sources = st.multiselect(
            "Sources à interroger",
            ["sirene", "bodacc", "datasubvention", "aides_territoires", "insee", "france2030"],
            default=["sirene", "bodacc"],
        )

        st.markdown("**Modèle LLM**")
        model = st.selectbox(
            "Modèle de raisonnement",
            ["qwen2.5:14b", "qwen2.5:7b", "llama3.2:latest", "mistral:latest"],
        )
else:
    territory = "hauts-de-france"
    sources = ["sirene", "bodacc"]
    model = None

# Launch button
if st.button("🚀 Lancer l'évaluation", type="primary", disabled=not question):
    with st.spinner("Évaluation en cours..."):
        progress_bar = st.progress(0, text="Initialisation...")
        status_container = st.empty()

        def update_status(status: WorkflowStatus, message: str):
            """Callback pour mise à jour du statut."""
            status_map = {
                WorkflowStatus.FRAMING: (10, "🎯 Cadrage de la question..."),
                WorkflowStatus.COLLECTING: (30, "📥 Collecte des données..."),
                WorkflowStatus.ANALYZING: (60, "📊 Analyse en cours..."),
                WorkflowStatus.GENERATING: (85, "📝 Génération du rapport..."),
                WorkflowStatus.AWAITING_VALIDATION: (100, "✅ Rapport prêt !"),
            }
            if status in status_map:
                progress, text = status_map[status]
                progress_bar.progress(progress, text=text)
            status_container.info(f"{status.value}: {message}")

        # Run workflow
        async def run_evaluation():
            workflow = EvaluationWorkflow(on_status_change=update_status)
            return await workflow.run(question)

        try:
            result = asyncio.run(run_evaluation())
            st.session_state.evaluation_result = result
            st.session_state.evaluation_status = result.status.value
            st.success("Évaluation terminée !")
            st.rerun()
        except Exception as e:
            st.error(f"Erreur: {e}")
            import traceback

            st.code(traceback.format_exc())

# Display results
if st.session_state.evaluation_result:
    result = st.session_state.evaluation_result

    st.divider()
    st.subheader("📋 Résultat de l'évaluation")

    # Status
    status_colors = {"awaiting_validation": "🟡", "validated": "🟢", "failed": "🔴"}
    st.write(f"**Statut**: {status_colors.get(result.status.value, '⚪')} {result.status.value}")

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📄 Rapport", "📊 Statistiques", "🔍 Détails"])

    with tab1:
        if result.report:
            st.markdown(result.report.markdown)

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("✅ Valider le rapport"):
                    st.success("Rapport validé !")
            with col2:
                st.download_button(
                    "📥 Télécharger (Markdown)",
                    result.report.markdown,
                    file_name=f"rapport_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                )
            with col3:
                st.button("📄 Export PDF", disabled=True, help="Bientôt disponible")

    with tab2:
        if result.analysis:
            st.json(result.analysis.statistics)
            st.markdown("**Insights clés:**")
            for insight in result.analysis.insights:
                st.write(f"• {insight}")

            if result.analysis.recommendations:
                st.markdown("**Recommandations:**")
                for rec in result.analysis.recommendations:
                    st.write(f"💡 {rec}")

    with tab3:
        if result.frame:
            st.markdown("**Sous-questions identifiées:**")
            for q in result.frame.sub_questions:
                st.write(f"• {q}")

            st.markdown("**Sources utilisées:**")
            if result.collection:
                st.write(f"Documents collectés: {result.collection.document_count}")
                st.write(f"Sources: {', '.join(result.collection.sources_used)}")
                if result.collection.errors:
                    st.warning(f"Erreurs: {result.collection.errors}")

        if result.errors:
            st.error(f"Erreurs du workflow: {result.errors}")

# Clear button
if st.session_state.evaluation_result:
    if st.button("🗑️ Nouvelle évaluation"):
        st.session_state.evaluation_result = None
        st.session_state.evaluation_status = None
        st.rerun()
