
import streamlit as st
from src.storage.db import init_db
from src.ui.theme import apply_theme

st.set_page_config(
    page_title="SAST Comparative Evaluation",
    page_icon="🛡️",
    layout="wide"
)

init_db()
apply_theme()

# Research workspace pages
PAGES = {
    "Overview": "research_pages.overview",
    "Dataset & Inputs": "research_pages.dataset",
    "Ground Truth": "research_pages.ground_truth",
    "Traditional SAST": "research_pages.traditional",
    "AI Analysis": "research_pages.ai_analysis",
    "Hybrid Analysis": "research_pages.hybrid",
    "Findings & Adjudication": "research_pages.findings",
    "Evaluation & Statistics": "research_pages.evaluation",
    "Reproducibility & Reports": "research_pages.reports",
    "Settings & Diagnostics": "research_pages.settings",
}

# Sidebar navigation
st.sidebar.title("🛡️ SAST Research Lab")
st.sidebar.caption("Comparative evaluation workspace")

selected = st.sidebar.radio(
    "Research workspace",
    list(PAGES.keys())
)

st.sidebar.divider()
st.sidebar.caption("Python 3.11 · Streamlit")
st.sidebar.caption("No empirical results are preloaded.")

# Load and render selected page
module = __import__(PAGES[selected], fromlist=["render"])
module.render()
