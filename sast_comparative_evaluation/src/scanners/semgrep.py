import json, shutil, subprocess, time
from pathlib import Path

def available():
    return shutil.which("semgrep") is not None

def version():
    if not available(): return None
    p = subprocess.run(["semgrep","--version"],capture_output=True,text=True,timeout=20)
    return (p.stdout or p.stderr).strip()

def scan(target_path, config="auto", timeout=900):
    if not available():
        raise RuntimeError("Semgrep CLI is not installed. Import a genuine Semgrep JSON report instead.")
    start = time.perf_counter()
    cmd = ["semgrep","scan","--json","--config",config,str(target_path)]
    p = subprocess.run(cmd,capture_output=True,text=True,timeout=timeout)
    elapsed = time.perf_counter()-start
    if p.returncode not in (0,1):
        raise RuntimeError(p.stderr[-3000:] or f"Semgrep exited with {p.returncode}")
    data = json.loads(p.stdout or "{}")
    return data, elapsed, cmd

def parse_report(data):
    out=[]
    for item in data.get("results",[]):
        extra=item.get("extra",{})
        meta=extra.get("metadata",{})
        cwe=meta.get("cwe",[])
        if isinstance(cwe,list): cwe=", ".join(map(str,cwe))
        out.append({
          "finding_id": item.get("check_id",""),
          "file_path": item.get("path",""),
          "start_line": item.get("start",{}).get("line",0),
          "end_line": item.get("end",{}).get("line",0),
          "cwe": cwe,
          "severity": extra.get("severity","unknown"),
          "title": item.get("check_id","Semgrep finding"),
          "description": extra.get("message",""),
          "evidence": extra.get("lines",""),
          "confidence": meta.get("confidence")
        })
    return out
