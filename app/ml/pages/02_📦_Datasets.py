"""Datasets - Gestion des jeux de données."""

import os

import streamlit as st

st.set_page_config(page_title="Datasets", page_icon="📦", layout="wide")

st.title("📦 Gestion des Datasets")

# Dataset list
datasets = [
    {"name": "mptoo_assistant_train", "size": "22 exemples", "format": "JSONL", "status": "✅"},
    {"name": "evaluation_qa", "size": "150 exemples", "format": "JSONL", "status": "✅"},
    {"name": "territorial_entities", "size": "5000+ entrées", "format": "JSON", "status": "🔄"},
]

st.subheader("📋 Datasets disponibles")

for ds in datasets:
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    with col1:
        st.write(f"**{ds['name']}**")
    with col2:
        st.write(ds["size"])
    with col3:
        st.write(ds["format"])
    with col4:
        st.write(ds["status"])

st.divider()

# Upload new dataset
st.subheader("📤 Importer un dataset")

uploaded = st.file_uploader("Fichier JSONL/JSON", type=["jsonl", "json"])

if uploaded:
    st.success(f"Fichier {uploaded.name} prêt à être importé")
    name = st.text_input("Nom du dataset")
    if st.button("✅ Importer"):
        st.success("Dataset importé !")

st.divider()

# Label Studio integration
st.subheader("🏷️ Label Studio")
st.info("Connexion à Label Studio pour l'annotation des données")
st.write(f"**URL:** {os.getenv('LABEL_STUDIO_URL', 'http://localhost:8085')}")
st.button("🔗 Ouvrir Label Studio")
