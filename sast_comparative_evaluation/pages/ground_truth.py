import streamlit as st, pandas as pd
from src.ui.theme import page_header
from src.storage.db import get_samples,upsert_ground_truth,get_ground_truth

def render():
    page_header("Ground truth","Record eligibility and traceable labels using CVE metadata, vulnerable/fixed revisions and patch evidence.")
    samples=get_samples(); existing=get_ground_truth()
    if not samples:
        st.info("Import a dataset manifest first."); return
    ids=[str(s["sample_id"]) for s in samples]
    sid=st.selectbox("Sample",ids)
    sample=next(s for s in samples if str(s["sample_id"])==sid)
    st.write({k:sample.get(k,"") for k in ("project","language","cve","cwe","vulnerable_commit","fixed_commit","affected_file")})
    old=existing.get(sid,{})
    with st.form("gt_form"):
        eligibility=st.selectbox("Eligibility decision",["pending","eligible","excluded"],index=["pending","eligible","excluded"].index(old.get("eligibility","pending")))
        status=st.selectbox("Ground-truth status",["unlabelled","vulnerable","negative"],index=["unlabelled","vulnerable","negative"].index(old.get("ground_truth_status","unlabelled")))
        cve=st.text_input("CVE identifier",old.get("cve",sample.get("cve","")))
        cwe=st.text_input("Documented CWE",old.get("cwe",sample.get("cwe","")))
        affected=st.text_input("Affected file / code region",old.get("affected_file",sample.get("affected_file","")))
        evidence=st.text_area("Evidence note: CVE record, patch, vulnerable/fixed code, source location",old.get("evidence_note",sample.get("evidence_note","")))
        reviewer=st.text_input("Reviewer / adjudicator",old.get("reviewer",""))
        independent=st.checkbox("Ambiguous case independently reviewed",value=old.get("independent_review",False))
        submitted=st.form_submit_button("Save ground-truth record")
    if submitted:
        upsert_ground_truth(sid,{"sample_id":sid,"eligibility":eligibility,"ground_truth_status":status,
          "cve":cve,"cwe":cwe,"affected_file":affected,"evidence_note":evidence,
          "reviewer":reviewer,"independent_review":independent})
        st.success("Ground-truth record saved.")
    st.warning("Unlabelled code is not a true negative. TN requires an eligible negative control. A TP must match the documented weakness mechanism and source evidence.")
    if existing:
        st.dataframe(pd.DataFrame([{"sample_id":k,**v} for k,v in existing.items()]),use_container_width=True)
