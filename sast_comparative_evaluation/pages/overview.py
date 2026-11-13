import streamlit as st
from src.ui.theme import page_header
from src.storage.db import get_samples,get_findings,get_ground_truth,get_runs

def render():
    page_header("Research overview","A controlled workspace for the manuscript's three-group SAST comparison.")
    samples=get_samples(); findings=get_findings(); gt=get_ground_truth(); runs=get_runs()
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Imported samples",len(samples))
    c2.metric("Ground-truth records",len(gt))
    c3.metric("Stored findings",len(findings))
    c4.metric("Recorded analysis runs",len(runs))
    st.subheader("Experimental design")
    st.markdown("""
    | Group | Experimental condition |
    |---|---|
    | A1 | Semgrep |
    | A2 | CodeQL |
    | A3 | Deduplicated Semgrep + CodeQL union |
    | B | One fixed-version LLM API; five repeated assessments per sample |
    | C1 | Hybrid union |
    | C2 | Consensus and evidence-validated outputs, reported separately |
    """)
    st.info("No empirical performance results are supplied. Metrics remain unavailable until genuine findings and ground-truth adjudications are recorded.")
    st.subheader("Recommended sequence")
    st.markdown("1. Import the OpenSSF CVE Benchmark manifest and source files.\n2. Verify eligibility and construct ground truth from CVE/patch evidence.\n3. Run/import Semgrep and CodeQL results.\n4. Run five controlled LLM assessments per eligible sample.\n5. Generate hybrid outputs, adjudicate findings, then calculate metrics and statistics.")
    st.warning("OWASP Benchmark is supplementary only and must be reported separately; its official suites target Java and Python, not the primary JavaScript/TypeScript sample.")
