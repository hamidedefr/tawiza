"""Progress tracker component for workflow status."""

from collections.abc import Callable
from typing import Optional

import streamlit as st


class ProgressTracker:
    """Visual progress tracker for evaluation workflow."""

    STAGES = [
        ("framing", "🎯 Cadrage", "Décomposition de la question"),
        ("collecting", "📥 Collecte", "Récupération des données"),
        ("analyzing", "📊 Analyse", "Traitement statistique"),
        ("generating", "📝 Rédaction", "Génération du rapport"),
        ("validation", "✅ Validation", "En attente de validation"),
    ]

    def __init__(self, container: st.container | None = None):
        self.container = container or st.container()
        self._current_stage = 0

    def update(self, stage: str, message: str = "") -> None:
        """Update progress to given stage."""
        stage_map = {s[0]: i for i, s in enumerate(self.STAGES)}
        self._current_stage = stage_map.get(stage, self._current_stage)

        with self.container:
            # Progress bar
            progress = (self._current_stage + 1) / len(self.STAGES)
            st.progress(progress)

            # Stage indicators
            cols = st.columns(len(self.STAGES))
            for i, (key, icon, desc) in enumerate(self.STAGES):
                with cols[i]:
                    if i < self._current_stage:
                        st.success(icon)
                    elif i == self._current_stage:
                        st.info(icon)
                    else:
                        st.write(icon)

            # Current message
            if message:
                st.write(f"*{message}*")

    def reset(self) -> None:
        """Reset progress tracker."""
        self._current_stage = 0
        self.container.empty()
