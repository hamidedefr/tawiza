"""MPtoO Admin - Panel d'administration."""

import streamlit as st

st.set_page_config(
    page_title="MPtoO Admin", page_icon="⚙️", layout="wide", initial_sidebar_state="expanded"
)

st.title("⚙️ MPtoO - Administration")

st.markdown("""
## Panel d'Administration

Bienvenue sur le panel d'administration MPtoO.

### Fonctionnalités

- 📊 **Dashboard** - Vue d'ensemble du système
- 🤖 **Agents** - Gestion et monitoring des agents IA
- 📁 **Sources** - Configuration des sources de données
- 👥 **Utilisateurs** - Gestion des accès
- 📋 **Logs** - Journaux système
""")

with st.sidebar:
    st.header("🔧 Configuration")
    st.info("Admin Panel v2.0")
