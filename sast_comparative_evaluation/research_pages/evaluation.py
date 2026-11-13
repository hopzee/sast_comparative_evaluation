import streamlit as st, pandas as pd
from src.ui.theme import page_header
from src.storage.db import get_samples,get_findings,get_ground_truth,get_adjudications
from src.evaluation.metrics import score_instances
from src.evaluation.statistics import mcnemar_test,bootstrap_mean_ci
import plotly.express as px

def render():
    page_header("Evaluation & statistics","Calculate metrics only from eligible, labelled samples and adjudicated findings.")
    samples=get_samples(); findings=get_findings(); gt=get_ground_truth(); adjud=get_adjudications()
    if not samples:
        st.info("Import samples and ground truth first."); return
    # Attach adjudication decisions to findings without mutating source records.
    enriched=[]
    for f in findings:
        x=dict(f); a=adjud.get(str(f.get("finding_id")),{})
        x["adjudication"]=a.get("decision",f.get("adjudication","pending"))
        enriched.append(x)
    methods=["Semgrep","CodeQL","Traditional union","LLM","Hybrid union","Hybrid consensus","Hybrid evidence candidate"]
    results={}
    for method in methods:
        if method=="Traditional union":
            subset=[f for f in enriched if f.get("tool") in ("Semgrep","CodeQL")]
        else: subset=[f for f in enriched if f.get("tool")==method]
        results[method]=score_instances(samples,subset,gt)
    st.subheader("Vulnerability-instance metrics")
    df=pd.DataFrame(results).T
    st.dataframe(df.style.format(precision=3),use_container_width=True)
    chart=df[["Precision","Recall","F1"]].copy()
    if chart.notna().any().any():
        st.plotly_chart(px.bar(chart,barmode="group",title="Measured metrics by method"),use_container_width=True)
    st.caption("Binary vulnerability-instance analysis. Finding-level correctness is separately represented by the adjudication register.")
    st.subheader("Paired comparison: manual input")
    st.caption("Enter paired 0/1 detection outcomes in identical sample order. Use McNemar only when the paired unit and eligible denominator are valid.")
    with st.expander("Run McNemar test on paired detection vectors"):
        a=st.text_input("Method A outcomes (comma-separated 0/1)")
        b=st.text_input("Method B outcomes (comma-separated 0/1)")
        if st.button("Calculate McNemar"):
            try:
                av=[int(x.strip()) for x in a.split(",") if x.strip()]
                bv=[int(x.strip()) for x in b.split(",") if x.strip()]
                if any(x not in (0,1) for x in av+bv): raise ValueError("Only 0 and 1 are allowed.")
                st.json(mcnemar_test(av,bv))
            except Exception as e: st.error(str(e))
    st.warning("The app does not infer TN from unlabelled samples. If the negative-control set is absent, TN-dependent metrics remain unavailable. Non-significance is not evidence of equivalence. For the manuscript's full protocol, use project/vulnerability-cluster bootstrap and Holm correction across predeclared comparisons.")
