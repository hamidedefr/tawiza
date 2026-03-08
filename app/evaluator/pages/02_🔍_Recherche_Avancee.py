"""Recherche Avancée - Agents S3 multi-sources."""

import asyncio
import json
import os
from datetime import datetime

import streamlit as st

# Import des agents avancés
from app.evaluator.advanced_agents import (
    AdvancedEvaluationWorkflow,
    AggregatedResult,
    SearchStatus,
    deep_search,
    quick_search,
)

# Configuration
st.set_page_config(page_title="Recherche Avancée", page_icon="🔍", layout="wide")

st.title("🔍 Recherche Avancée S3")
st.caption("Agents de recherche multi-sources: Web, Crawling, Vectoriel")

# Configuration display
with st.expander("⚙️ Configuration", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        st.code(f"Ollama: {os.getenv('OLLAMA_URL', 'http://localhost:11434')}")
        st.code(f"Qdrant: {os.getenv('QDRANT_URL', 'http://mptoo-qdrant:6333')}")
    with col2:
        st.code(f"Modèle: {os.getenv('LLM_MODEL', 'qwen3-coder:30b')}")
        st.code(f"SearXNG: {os.getenv('SEARXNG_URL', 'http://localhost:8888')}")

# Session state
if "search_result" not in st.session_state:
    st.session_state.search_result = None
if "search_history" not in st.session_state:
    st.session_state.search_history = []

# Search form
st.subheader("Votre recherche")

query = st.text_input(
    "Question ou termes de recherche",
    placeholder="Ex: Impact des startups France 2030 sur l'emploi en Hauts-de-France",
)

# Options
col1, col2, col3 = st.columns(3)
with col1:
    search_mode = st.radio(
        "Mode de recherche",
        ["⚡ Rapide", "🔬 Approfondi"],
        help="Rapide: Web uniquement | Approfondi: Web + Crawling + Vectoriel",
    )

with col2:
    web_results = st.slider("Résultats web", 3, 20, 10)

with col3:
    enable_crawling = st.checkbox("Activer le crawling", value=search_mode == "🔬 Approfondi")
    enable_vector = st.checkbox("Recherche vectorielle", value=True)

# Search button
if st.button("🚀 Lancer la recherche", type="primary", disabled=not query):
    with st.spinner("Recherche en cours..."):
        progress_bar = st.progress(0, text="Initialisation...")
        status_container = st.empty()

        def update_status(status: SearchStatus, message: str):
            """Callback pour mise à jour du statut."""
            status_map = {
                SearchStatus.SEARCHING_WEB: (20, "🌐 Recherche web..."),
                SearchStatus.CRAWLING: (50, "🕷️ Crawling des pages..."),
                SearchStatus.VECTOR_SEARCH: (70, "🧠 Recherche sémantique..."),
                SearchStatus.SYNTHESIZING: (90, "✨ Synthèse..."),
                SearchStatus.COMPLETED: (100, "✅ Terminé !"),
            }
            if status in status_map:
                progress, text = status_map[status]
                progress_bar.progress(progress, text=text)
            status_container.info(f"{status.value}: {message}")

        async def run_search():
            workflow = AdvancedEvaluationWorkflow(on_status_change=update_status)
            return await workflow.run(
                query,
                {
                    "web_results": web_results,
                    "enable_crawling": enable_crawling,
                    "enable_vector_search": enable_vector,
                },
            )

        try:
            result = asyncio.run(run_search())
            st.session_state.search_result = result
            st.session_state.search_history.append(
                {
                    "query": query,
                    "timestamp": datetime.now().isoformat(),
                    "total_docs": result.total_documents,
                }
            )
            st.success(f"Recherche terminée en {result.search_time_seconds:.1f}s")
            st.rerun()
        except Exception as e:
            st.error(f"Erreur: {e}")
            import traceback

            st.code(traceback.format_exc())

# Display results
if st.session_state.search_result:
    result = st.session_state.search_result

    st.divider()

    # Stats row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Documents trouvés", result.total_documents)
    with col2:
        st.metric("Sources web", len(result.web_results))
    with col3:
        st.metric("Pages crawlées", len(result.crawl_results))
    with col4:
        st.metric("Docs vectoriels", len(result.vector_results))

    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Synthèse", "🌐 Web", "🕷️ Crawl", "🧠 Vectoriel"])

    with tab1:
        st.subheader("Synthèse des résultats")

        if result.synthesis:
            try:
                synthesis_data = json.loads(result.synthesis)

                # Summary
                st.markdown(f"**Résumé:** {synthesis_data.get('summary', 'N/A')}")

                # Key points
                st.markdown("**Points clés:**")
                for point in synthesis_data.get("key_points", []):
                    st.write(f"• {point}")

                # Confidence
                confidence = synthesis_data.get("confidence", 0)
                st.progress(confidence, text=f"Confiance: {confidence * 100:.0f}%")

                # Recommendations
                if synthesis_data.get("recommendations"):
                    st.markdown("**Recommandations:**")
                    for rec in synthesis_data.get("recommendations", []):
                        st.info(f"💡 {rec}")

            except json.JSONDecodeError:
                st.markdown(result.synthesis)

        # Sources used
        st.caption(f"Sources utilisées: {', '.join(result.sources_used)}")

    with tab2:
        st.subheader("Résultats de recherche web")

        if result.web_results:
            for i, r in enumerate(result.web_results):
                with st.expander(f"🔗 {r.title or 'Sans titre'}", expanded=i < 3):
                    st.markdown(f"**URL:** [{r.url}]({r.url})")
                    st.markdown(f"**Source:** {r.source} | **Score:** {r.score:.2f}")
                    st.markdown(f"**Extrait:** {r.snippet}")
        else:
            st.info("Aucun résultat web trouvé")

    with tab3:
        st.subheader("Pages crawlées")

        if result.crawl_results:
            for r in result.crawl_results:
                with st.expander(f"📄 {r.title or r.url}"):
                    st.markdown(f"**URL:** [{r.url}]({r.url})")
                    if r.error:
                        st.error(f"Erreur: {r.error}")
                    else:
                        st.markdown(f"**Contenu:** {r.content[:1000]}...")
                        if r.metadata:
                            st.json(r.metadata)
                        st.caption(f"Liens trouvés: {len(r.links)}")
        else:
            st.info("Aucune page crawlée")

    with tab4:
        st.subheader("Recherche sémantique (Qdrant)")

        if result.vector_results:
            for r in result.vector_results:
                with st.expander(f"📊 Score: {r.score:.3f}"):
                    st.markdown(f"**ID:** {r.id}")
                    st.markdown(f"**Contenu:** {r.content[:500]}...")
                    if r.metadata:
                        st.json(r.metadata)
        else:
            st.info("Aucun résultat vectoriel - La collection Qdrant est peut-être vide")

    # Export
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Exporter JSON"):
            export_data = {
                "query": result.query,
                "timestamp": datetime.now().isoformat(),
                "stats": {
                    "total_documents": result.total_documents,
                    "search_time": result.search_time_seconds,
                    "sources": result.sources_used,
                },
                "synthesis": result.synthesis,
                "web_results": [
                    {"title": r.title, "url": r.url, "snippet": r.snippet}
                    for r in result.web_results
                ],
                "crawl_results": [
                    {"url": r.url, "title": r.title, "content": r.content[:1000]}
                    for r in result.crawl_results
                ],
            }
            st.download_button(
                "💾 Télécharger",
                json.dumps(export_data, ensure_ascii=False, indent=2),
                file_name=f"recherche_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",
            )

    with col2:
        if st.button("🗑️ Nouvelle recherche"):
            st.session_state.search_result = None
            st.rerun()

# History
if st.session_state.search_history:
    with st.sidebar:
        st.subheader("📜 Historique")
        for h in reversed(st.session_state.search_history[-10:]):
            st.caption(f"• {h['query'][:30]}... ({h['total_docs']} docs)")
