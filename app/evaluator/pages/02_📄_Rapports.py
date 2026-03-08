"""Page de gestion des rapports."""

import streamlit as st

st.set_page_config(page_title="Rapports", page_icon="📄", layout="wide")

st.title("📄 Historique des Rapports")

st.info("Cette page affichera l'historique des évaluations et rapports générés.")

# Placeholder for reports list
st.markdown("""
### Fonctionnalités à venir

- 📋 Liste des évaluations passées
- 🔍 Recherche par date, territoire, thématique
- 📊 Statistiques d'utilisation
- 📥 Export groupé
""")

# Demo data
st.subheader("Évaluations récentes")

demo_data = [
    {"date": "2024-12-08", "question": "Impact France 2030 en HdF", "statut": "✅ Validé"},
    {"date": "2024-12-07", "question": "Subventions ESS en IDF", "statut": "🟡 En attente"},
    {"date": "2024-12-05", "question": "Créations entreprises tech", "statut": "✅ Validé"},
]

for item in demo_data:
    with st.expander(f"{item['date']} - {item['question']}"):
        st.write(f"**Statut:** {item['statut']}")
        col1, col2 = st.columns(2)
        with col1:
            st.button("📄 Voir", key=f"view_{item['date']}")
        with col2:
            st.button("📥 Télécharger", key=f"dl_{item['date']}")
