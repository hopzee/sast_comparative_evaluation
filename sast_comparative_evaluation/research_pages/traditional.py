import json
import streamlit as st
import pandas as pd
from pathlib import Path
from src.ui.theme import page_header
from src.storage.db import get_samples, add_finding, get_findings
from src.scanners import semgrep, codeql
from src.data.schema import normalize_finding


def _save(rows, tool, sample_id, variant, elapsed=None):
    for i, raw in enumerate(rows):
        raw = dict(raw)
        raw["tool"] = tool
        raw["sample_id"] = sample_id
        raw["variant"] = variant
        if elapsed is not None:
            raw["runtime_seconds"] = elapsed
        finding = normalize_finding(raw, tool, sample_id)
        finding["variant"] = variant
        if not finding["finding_id"]:
            finding["finding_id"] = f"{tool}-{sample_id}-{variant}-{i}-{finding['file_path']}-{finding['start_line']}"
        add_finding(finding["finding_id"], tool, sample_id, finding)


def _resolve(path, root):
    p = Path(path)
    if not p.is_absolute():
        p = Path(root) / p
    return str(p.resolve())


def render():
    page_header("Traditional SAST", "Run Semgrep and CodeQL where installed, or import their authentic native reports.")
    c1, c2 = st.columns(2)
    c1.metric("Semgrep CLI", "Available" if semgrep.available() else "Not installed")
    c1.caption(semgrep.version() or "Import JSON if unavailable.")
    c2.metric("CodeQL CLI", "Available" if codeql.available() else "Not installed")
    c2.caption(codeql.version() or "Import SARIF if unavailable.")

    samples = get_samples()
    if not samples:
        st.info("Import the sample manifest first.")
        return
    sample_ids = [str(s["sample_id"]) for s in samples]
    sample_id = st.selectbox("Benchmark sample", sample_ids)
    sample = next(s for s in samples if str(s["sample_id"]) == sample_id)
    variant = st.selectbox("Code revision", ["vulnerable", "fixed"])
    path_field = "vulnerable_path" if variant == "vulnerable" else "fixed_path"
    root = st.text_input("Source root (used for relative manifest paths)", st.session_state.get("source_root", "data/raw/benchmark"))
    target = _resolve(str(sample.get(path_field, "")), root)
    st.caption(f"Selected source: {target}")
    if not Path(target).exists():
        st.warning("The selected source path is not present in this runtime. Check the manifest paths or upload/extract the source archive.")

    with st.expander("Run Semgrep"):
        config = st.text_input("Semgrep config / ruleset", "auto")
        if st.button("Run Semgrep on selected sample/revision"):
            try:
                with st.spinner("Running Semgrep..."):
                    data, elapsed, cmd = semgrep.scan(target, config)
                rows = semgrep.parse_report(data)
                _save(rows, "Semgrep", sample_id, variant, elapsed)
                st.success(f"Semgrep completed: {len(rows)} findings in {elapsed:.2f}s.")
                st.session_state["semgrep_raw"] = data
            except Exception as e:
                st.error(str(e))

    with st.expander("Run CodeQL"):
        st.caption("CodeQL uses the JavaScript database language for JavaScript and TypeScript projects.")
        suite = st.text_input("Query suite", "codeql/javascript-queries:codeql-suites/javascript-security-extended.qls")
        if st.button("Create CodeQL database and analyze selected sample/revision"):
            try:
                codeql_root = str(Path(target).parent) if Path(target).is_file() else target
                with st.spinner("Running CodeQL (may take several minutes)..."):
                    data, elapsed, cmd = codeql.analyze(codeql_root, "javascript", suite)
                rows = codeql.parse_sarif(data)
                _save(rows, "CodeQL", sample_id, variant, elapsed)
                st.success(f"CodeQL completed: {len(rows)} findings in {elapsed:.2f}s.")
                st.session_state["codeql_raw"] = data
            except Exception as e:
                st.error(str(e))

    st.subheader("Import native scanner output")
    st.caption("The imported report is assigned to the sample and revision selected above. Import one sample/revision report at a time to preserve the evaluation unit.")
    a, b = st.columns(2)
    with a:
        up = st.file_uploader("Semgrep JSON", type=["json"], key="sg_json")
        if up and st.button("Import Semgrep JSON"):
            try:
                data = json.load(up)
                rows = semgrep.parse_report(data)
                _save(rows, "Semgrep", sample_id, variant)
                st.success(f"Imported {len(rows)} Semgrep findings for {sample_id} ({variant}).")
            except Exception as e:
                st.error(str(e))
    with b:
        up2 = st.file_uploader("CodeQL SARIF", type=["sarif", "json"], key="cq_sarif")
        if up2 and st.button("Import CodeQL SARIF"):
            try:
                data = json.load(up2)
                rows = codeql.parse_sarif(data)
                _save(rows, "CodeQL", sample_id, variant)
                st.success(f"Imported {len(rows)} CodeQL findings for {sample_id} ({variant}).")
            except Exception as e:
                st.error(str(e))

    findings = get_findings()
    st.subheader("Stored traditional findings")
    df = pd.DataFrame([f for f in findings if f.get("tool") in ("Semgrep", "CodeQL")])
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No scanner findings stored yet. Missing scanner binaries are never simulated.")
