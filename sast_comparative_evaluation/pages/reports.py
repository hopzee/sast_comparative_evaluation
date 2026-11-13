import streamlit as st, pandas as pd, json, hashlib, platform, sys
from src.ui.theme import page_header
from src.storage.db import export_all,get_samples,get_findings,get_runs
from src.reporting.export import build_experiment_zip
from src.evaluation.metrics import score_instances
from src.storage.db import get_ground_truth,get_adjudications

def render():
    page_header("Reproducibility & reports","Export the full experiment record, manifests, normalized findings and environment details.")
    data=export_all()
    st.metric("Stored records",len(data["samples"])+len(data["findings"])+len(data["runs"]))
    st.download_button("Download complete experiment archive (.zip)",build_experiment_zip(),
      "sast_experiment_records.zip","application/zip",type="primary")
    st.download_button("Download experiment JSON",json.dumps(data,indent=2,default=str).encode(),
      "experiment_export.json","application/json")
    st.subheader("Environment record")
    env={"python":sys.version,"platform":platform.platform(),"machine":platform.machine(),
         "processor":platform.processor()}
    st.json(env)
    st.download_button("Download environment.txt","\n".join(f"{k}: {v}" for k,v in env.items()),
      "environment.txt","text/plain")
    st.subheader("Result release gate")
    checks=[
      "Dataset extracted and exact repository commit recorded",
      "Eligible sample count and exclusion reasons documented",
      "Vulnerable/fixed source files and SHA-256 hashes retained",
      "Semgrep and CodeQL versions/configurations and raw outputs retained",
      "Fixed LLM model, prompt, parameters, API version and five runs recorded",
      "Ground truth and ambiguous cases independently adjudicated",
      "Hybrid union, consensus and evidence-validated outputs retained separately",
      "Metrics, denominators, confidence intervals and statistical tests verified",
      "All result tables and figures populated from reproducible records",
    ]
    for c in checks: st.checkbox(c,key="gate_"+hashlib.md5(c.encode()).hexdigest()[:8])
    st.warning("The manuscript's empirical release gate must be satisfied before presenting the study as a completed empirical evaluation.")
