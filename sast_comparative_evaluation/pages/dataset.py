import streamlit as st, pandas as pd
from pathlib import Path
from src.ui.theme import page_header
from src.data.io import read_manifest,safe_extract_zip,source_inventory,sha256_file
from src.storage.db import upsert_sample,get_samples

def render():
    page_header("Dataset & Inputs","Import the OpenSSF CVE Benchmark manifest and prepare identical vulnerable/fixed inputs.")
    st.markdown("**Primary dataset:** OpenSSF CVE Benchmark, restricted to eligible JavaScript/TypeScript cases. OWASP Benchmark must remain a separate supplementary experiment.")
    manifest=st.file_uploader("Upload dataset_manifest.csv",type=["csv"])
    if manifest and st.button("Validate and import manifest",type="primary"):
        try:
            df=read_manifest(manifest)
            count=0
            for row in df.to_dict("records"):
                upsert_sample(str(row["sample_id"]),row); count+=1
            st.success(f"Imported {count} unique sample records.")
        except Exception as e: st.error(str(e))
    st.subheader("Optional source archive")
    archive=st.file_uploader("Upload a ZIP containing benchmark source files",type=["zip"],key="source_zip")
    if archive and st.button("Safely extract source archive"):
        try:
            path=safe_extract_zip(archive,"data/raw/benchmark")
            st.session_state["source_root"]=str(path)
            files=source_inventory(path)
            st.success(f"Extracted source archive. Found {len(files)} JS/TS source files.")
            st.caption(f"Source root: {path}")
        except Exception as e: st.error(str(e))
    samples=get_samples()
    if samples:
        df=pd.DataFrame(samples)
        st.subheader(f"Imported manifest ({len(df)} records)")
        st.dataframe(df,use_container_width=True)
        st.download_button("Download current manifest CSV",df.to_csv(index=False).encode(), "dataset_manifest.csv","text/csv")
    root=st.session_state.get("source_root")
    if root:
        paths=source_inventory(root)
        if st.button("Generate source SHA-256 inventory"):
            rows=[]
            for p in paths:
                rows.append({"file_path":str(p.relative_to(root)),"sha256":sha256_file(p),"bytes":p.stat().st_size})
            out=pd.DataFrame(rows)
            st.dataframe(out,use_container_width=True)
            st.download_button("Download input hashes",out.to_csv(index=False).encode(),"input_hashes.csv","text/csv")
    with st.expander("Manifest schema"):
        st.code("sample_id, project, language, vulnerable_path, fixed_path, vulnerable_commit, fixed_commit, cve, cwe, repository_url, affected_file, eligibility, ground_truth_status, evidence_note, split",language="text")
