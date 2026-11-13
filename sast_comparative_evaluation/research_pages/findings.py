import streamlit as st
import pandas as pd
from src.ui.theme import page_header
from src.storage.db import get_findings, save_adjudication, get_adjudications, add_finding, get_samples


def render():
    page_header("Findings & adjudication", "Normalize, inspect and manually validate each finding against the documented vulnerability mechanism.")
    findings = get_findings()
    if not findings:
        st.info("No findings yet. Run/import scanner and AI outputs first.")
        return
    df = pd.DataFrame(findings)
    tools = ["All"] + sorted(df["tool"].dropna().unique().tolist())
    selected = st.selectbox("Filter by method", tools)
    view = df if selected == "All" else df[df["tool"] == selected]
    st.dataframe(view, use_container_width=True)
    ids = view["finding_id"].astype(str).tolist()
    fid = st.selectbox("Finding to adjudicate or assign", ids)
    finding = next(x for x in findings if str(x.get("finding_id")) == fid)
    old = get_adjudications().get(fid, {})
    st.json({k: finding.get(k) for k in ("tool", "sample_id", "variant", "file_path", "start_line", "end_line", "cwe", "severity", "title", "description", "evidence")})
    samples = get_samples()
    sample_ids = [str(s["sample_id"]) for s in samples]
    current_sid = str(finding.get("sample_id") or (sample_ids[0] if sample_ids else ""))
    if current_sid not in sample_ids and sample_ids:
        current_sid = sample_ids[0]
    with st.form("adjudicate"):
        assigned_sample = st.selectbox("Assign finding to benchmark sample", sample_ids,
            index=sample_ids.index(current_sid) if current_sid in sample_ids else 0)
        variant_options = ["unknown", "vulnerable", "fixed"]
        current_variant = finding.get("variant", "unknown")
        if current_variant not in variant_options:
            current_variant = "unknown"
        variant = st.selectbox("Revision represented", variant_options, index=variant_options.index(current_variant))
        decision = st.selectbox("Reviewer decision", ["pending", "TP", "FP", "not_applicable", "needs_review"],
            index=["pending", "TP", "FP", "not_applicable", "needs_review"].index(old.get("decision", "pending")))
        mechanism = st.text_area("Does the finding match the documented weakness mechanism?", old.get("mechanism", ""))
        evidence = st.text_area("Source evidence and rationale", old.get("evidence", ""))
        reviewer = st.text_input("Reviewer", old.get("reviewer", ""))
        save = st.form_submit_button("Save assignment and adjudication")
    if save:
        finding["sample_id"] = assigned_sample
        finding["variant"] = variant
        add_finding(fid, finding.get("tool", "Unknown"), assigned_sample, finding)
        save_adjudication(fid, {"decision": decision, "mechanism": mechanism, "evidence": evidence, "reviewer": reviewer})
        st.success("Sample assignment and adjudication saved.")
    st.info("A true positive needs vulnerability-mechanism agreement and sufficient source evidence. Same file or broad CWE alone is insufficient.")
