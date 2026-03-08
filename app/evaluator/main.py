"""MPtoO Evaluator - Application d'évaluation territoriale."""

import streamlit as st

st.set_page_config(
    page_title="MPtoO Évaluateur", page_icon="📊", layout="wide", initial_sidebar_state="expanded"
)

st.title("🏛️ MPtoO - Plateforme d'Évaluation Territoriale")

st.markdown("""
## Bienvenue sur MPtoO

Cette plateforme permet aux évaluateurs de politiques publiques de :

1. **Saisir une problématique d'évaluation** - Posez votre question d'évaluation
2. **Collecte automatique** - Le système récupère et analyse les données
3. **Validation du rapport** - Relisez et validez le rapport structuré
4. **Export** - Exportez en PDF ou DOCX

### Comment commencer ?

Utilisez le menu de gauche pour naviguer vers **📊 Évaluation** et lancer une nouvelle analyse.
""")

# Sidebar info
with st.sidebar:
    st.header("📌 Informations")
    st.info("Version: 2.0.0")
    st.success("Système opérationnel")
