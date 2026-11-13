import streamlit as st
import pandas as pd
import uuid
from pathlib import Path
from src.ui.theme import page_header
from src.storage.db import get_samples, add_run, add_finding, get_runs
from src.ai.client import get_config, analyze_source


def render():
    page_header("AI-driven analysis", "One fixed-version LLM API, standardized prompt, controlled source context and five repeated assessments.")
    cfg = get_config()
    st.write({"API base URL": cfg["base"], "Model configured": bool(cfg["model"]),
              "API key configured": bool(cfg["key"]), "Model ID": cfg["model"] or "Not configured"})
    st.warning("Do not provide CVE labels, patch descriptions, expected outcomes, ground-truth status or fix diffs to the model. Analyze the vulnerable and fixed revisions as blinded inputs.")
    samples = get_samples()
    if not samples:
        st.info("Import the sample manifest first.")
        return
    sid = st.selectbox("Select one sample", [str(s["sample_id"]) for s in samples])
    sample = next(s for s in samples if str(s["sample_id"]) == sid)
    variant = st.selectbox("Code revision to assess", ["vulnerable", "fixed"])
    path_field = "vulnerable_path" if variant == "vulnerable" else "fixed_path"
    source_path = st.text_input("Source file path", sample.get(path_field, ""))
    language = str(sample.get("language", "javascript")).lower()
    if language not in ("javascript", "typescript", "js", "ts"):
        language = "javascript"
    temperature = st.number_input("Temperature", min_value=0.0, max_value=2.0, value=0.0, step=0.1)
    max_tokens = st.number_input("Maximum output tokens", min_value=200, max_value=8000, value=1200, step=100)
    if st.button("Run five blinded AI assessments", type="primary"):
        try:
            source = Path(source_path).read_text(encoding="utf-8", errors="replace")
            if not source.strip():
                raise ValueError("Selected source file is empty.")
            for i in range(5):
                with st.spinner(f"LLM assessment {i+1}/5 ({variant} revision)..."):
                    result = analyze_source(source, Path(source_path).name, language, temperature, max_tokens)
                run_id = str(uuid.uuid4())
                record = {"run_id": run_id, "sample_id": sid, "variant": variant, "tool": "LLM", "repeat": i+1, **result}
                add_run(run_id, sid, "LLM", record)
                parsed = result["parsed"]
                for j, item in enumerate(parsed.get("findings", [])):
                    fid = f"LLM-{sid}-{variant}-{i+1}-{j}-{uuid.uuid4().hex[:8]}"
                    finding = {"finding_id": fid, "tool": "LLM", "sample_id": sid, "variant": variant, **item,
                      "description": item.get("explanation", ""), "raw_reference": run_id,
                      "adjudication": "pending", "runtime_seconds": result["latency_seconds"]}
                    add_finding(fid, "LLM", sid, finding)
            st.success(f"Five assessments completed for {sid} ({variant}) and recorded with raw provider responses.")
        except Exception as e:
            st.error(str(e))
    st.subheader("Recorded AI runs")
    runs = [r for r in get_runs("LLM") if str(r.get("sample_id")) == sid and r.get("variant") == variant]
    if runs:
        display = [{k: v for k, v in r.items() if k != "raw_response"} for r in runs]
        st.dataframe(pd.DataFrame(display), use_container_width=True)
        with st.expander("Inspect retained raw provider response"):
            st.json(runs[-1].get("raw_response", {}))
    else:
        st.info("No AI assessments recorded for this sample/revision.")
    st.caption("The adapter expects an OpenAI-compatible /chat/completions endpoint. Verify exact model snapshot, provider API version and terms.")
