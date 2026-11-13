import streamlit as st, platform, sys
from src.ui.theme import page_header
from src.storage.db import DB_PATH
from src.scanners.semgrep import available as semgrep_available, version as semgrep_version
from src.scanners.codeql import available as codeql_available, version as codeql_version
from src.ai.client import get_config


def render():
    page_header("Settings & diagnostics", "Check scanner availability, LLM configuration and local persistence.")
    st.subheader("Runtime")
    st.write({"Python": sys.version.split()[0], "Platform": platform.platform(), "SQLite file": str(DB_PATH)})
    st.subheader("Scanner tools")
    st.write({"Semgrep installed": semgrep_available(), "Semgrep version": semgrep_version(),
              "CodeQL installed": codeql_available(), "CodeQL version": codeql_version()})
    st.subheader("LLM API configuration")
    cfg = get_config()
    st.write({"Base URL": cfg["base"], "API key present": bool(cfg["key"]),
              "Model": cfg["model"] or "Not configured", "API version": cfg["api_version"] or "Not recorded"})
    st.code('''# Add to Streamlit Cloud > App > Settings > Secrets
LLM_API_KEY = "your-secret-key"
LLM_BASE_URL = "https://api.openai.com/v1"
LLM_MODEL = "exact-model-snapshot"
LLM_API_VERSION = "provider-api-version"''')
    st.error("Never paste API keys into source files or commit them to GitHub.")
    st.subheader("Persistence warning")
    st.warning("SQLite is stored on the app filesystem. Streamlit Community Cloud may reset local files during rebuilds/restarts. Download experiment archives regularly; use a managed database for durable production research records.")
