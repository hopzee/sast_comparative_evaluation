import streamlit as st
from src.storage.db import init_db
from src.ui.theme import apply_theme

st.set_page_config(page_title="SAST Comparative Evaluation", page_icon="🛡️", layout="wide")
init_db()
apply_theme()

PAGES = {
    "Overview": "pages.overview",
    "Dataset & Inputs": "pages.dataset",
    "Ground Truth": "pages.ground_truth",
    "Traditional SAST": "pages.traditional",
    "AI Analysis": "pages.ai_analysis",
    "Hybrid Analysis": "pages.hybrid",
    "Findings & Adjudication": "pages.findings",
    "Evaluation & Statistics": "pages.evaluation",
    "Reproducibility & Reports": "pages.reports",
    "Settings & Diagnostics": "pages.settings",
}

st.sidebar.title("🛡️ SAST Research Lab")
st.sidebar.caption("Comparative evaluation workspace")
selected = st.sidebar.radio("Research workspace", list(PAGES))
st.sidebar.divider()
st.sidebar.caption("Python 3.11 · Streamlit")
st.sidebar.caption("No empirical results are preloaded.")

module = __import__(PAGES[selected], fromlist=["render"])
module.render()
