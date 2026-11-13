import json, shutil, subprocess, time
from pathlib import Path

def available():
    return shutil.which("codeql") is not None

def version():
    if not available(): return None
    p=subprocess.run(["codeql","version"],capture_output=True,text=True,timeout=20)
    return (p.stdout or p.stderr).strip()

def analyze(target_path, language="javascript", query_suite="codeql/javascript-queries:codeql-suites/javascript-security-extended.qls", work_dir="data/codeql_work", timeout=1800):
    if not available():
        raise RuntimeError("CodeQL CLI is not installed. Import a genuine CodeQL SARIF report instead.")
    target=Path(target_path).resolve()
    work=Path(work_dir); work.mkdir(parents=True,exist_ok=True)
    db=work/"database"
    if db.exists():
        import shutil as sh; sh.rmtree(db)
    start=time.perf_counter()
    create=["codeql","database","create",str(db),"--language="+language,"--source-root",str(target),"--overwrite"]
    p=subprocess.run(create,capture_output=True,text=True,timeout=timeout)
    if p.returncode: raise RuntimeError(p.stderr[-3000:])
    sarif=work/"codeql.sarif"
    analyze_cmd=["codeql","database","analyze",str(db),query_suite,"--format=sarif-latest","--output",str(sarif)]
    p=subprocess.run(analyze_cmd,capture_output=True,text=True,timeout=timeout)
    if p.returncode: raise RuntimeError(p.stderr[-3000:])
    return json.loads(sarif.read_text(encoding="utf-8")), time.perf_counter()-start, create+analyze_cmd

def parse_sarif(data):
    findings=[]
    for run in data.get("runs",[]):
      rules={r.get("id"):r for r in run.get("tool",{}).get("driver",{}).get("rules",[])}
      for result in run.get("results",[]):
        loc=(result.get("locations") or [{}])[0].get("physicalLocation",{})
        region=loc.get("region",{})
        artifact=loc.get("artifactLocation",{})
        rule=rules.get(result.get("ruleId"),{})
        props=result.get("properties",{}) or {}
        msg=result.get("message",{}).get("text","")
        findings.append({
          "finding_id":result.get("ruleId",""),
          "file_path":artifact.get("uri",""),
          "start_line":region.get("startLine",0),
          "end_line":region.get("endLine",region.get("startLine",0)),
          "cwe":", ".join(props.get("tags",[])) if isinstance(props.get("tags",[]),list) else "",
          "severity":result.get("level","unknown"),
          "title":rule.get("shortDescription",{}).get("text",result.get("ruleId","CodeQL finding")),
          "description":msg,"evidence":"","confidence":None
        })
    return findings
