import io, json, zipfile
import pandas as pd
from src.storage.db import export_all

def build_experiment_zip():
    data=export_all()
    buffer=io.BytesIO()
    with zipfile.ZipFile(buffer,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("experiment_export.json",json.dumps(data,indent=2,default=str))
        for name,rows in [("samples.csv",data["samples"]),("findings.csv",data["findings"]),("runs.csv",data["runs"])]:
            z.writestr(name,pd.DataFrame(rows).to_csv(index=False))
        z.writestr("ground_truth.json",json.dumps(data["ground_truth"],indent=2))
        z.writestr("adjudications.json",json.dumps(data["adjudications"],indent=2))
    return buffer.getvalue()

def make_metrics_csv(metrics_by_tool):
    return pd.DataFrame(metrics_by_tool).T.to_csv().encode("utf-8")
