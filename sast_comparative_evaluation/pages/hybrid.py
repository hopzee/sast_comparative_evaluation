import streamlit as st, pandas as pd, uuid
from src.ui.theme import page_header
from src.storage.db import get_findings,add_finding
from src.hybrid.build import build_hybrid

def render():
    page_header("Hybrid analysis","Keep union, consensus and evidence-validated candidate findings distinct.")
    findings=get_findings()
    if not findings:
        st.info("Run or import traditional and/or AI findings first."); return
    if st.button("Build hybrid outputs",type="primary"):
        result=build_hybrid(findings)
        for label,key in [("Hybrid union","union"),("Hybrid consensus","consensus"),("Hybrid evidence candidate","evidence_candidates")]:
            for i,f in enumerate(result[key]):
                x=dict(f); x["finding_id"]=f"H-{label}-{uuid.uuid4().hex[:10]}"; x["tool"]=label
                add_finding(x["finding_id"],label,x.get("sample_id"),x)
        st.success(f"Generated {len(result['union'])} union, {len(result['consensus'])} consensus and {len(result['evidence_candidates'])} evidence-candidate records.")
        st.session_state["hybrid_preview"]=result
    result=st.session_state.get("hybrid_preview")
    if result:
        tabs=st.tabs(["Union","Consensus","Evidence candidates"])
        for tab,key in zip(tabs,["union","consensus","evidence_candidates"]):
            with tab:
                df=pd.DataFrame(result[key])
                if not df.empty: st.dataframe(df,use_container_width=True)
                else: st.info("No records in this output.")
    st.warning("Consensus means traditional and AI findings align under the matching rule. Evidence candidates are not automatically confirmed true positives; reviewer adjudication remains mandatory. AI disagreement must not erase traditional alerts.")
