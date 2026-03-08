"""Report viewer component."""

from datetime import datetime
from typing import Optional

import streamlit as st


class ReportViewer:
    """Component for displaying and interacting with reports."""

    def __init__(self, container: st.container | None = None):
        self.container = container or st.container()

    def display(
        self,
        markdown: str,
        title: str = "Rapport",
        evaluation_id: str | None = None,
        on_validate: callable | None = None,
        on_export: callable | None = None,
    ) -> None:
        """Display a report with actions."""
        with self.container:
            st.subheader(f"📄 {title}")

            if evaluation_id:
                st.caption(f"ID: {evaluation_id}")

            # Tabs for different views
            tab1, tab2 = st.tabs(["📖 Lecture", "📝 Markdown"])

            with tab1:
                st.markdown(markdown)

            with tab2:
                st.code(markdown, language="markdown")

            # Action buttons
            st.divider()
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if st.button("✅ Valider", type="primary"):
                    if on_validate:
                        on_validate()
                    st.success("Rapport validé !")

            with col2:
                st.download_button(
                    "📥 Markdown",
                    markdown,
                    file_name=f"rapport_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown",
                )

            with col3:
                if st.button("📄 PDF", disabled=True):
                    pass

            with col4:
                if st.button("📑 DOCX", disabled=True):
                    pass

    def display_error(self, error: str) -> None:
        """Display error state."""
        with self.container:
            st.error(f"Erreur lors de la génération du rapport: {error}")
            st.button("🔄 Réessayer")
