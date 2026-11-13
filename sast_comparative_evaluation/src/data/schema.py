FINDING_FIELDS = [
 "finding_id","tool","sample_id","repository","file_path","start_line","end_line",
 "cwe","severity","title","description","evidence","confidence","runtime_seconds",
 "raw_reference","adjudication"
]

def normalize_finding(raw, tool, sample_id=None):
    return {
      "finding_id": str(raw.get("finding_id") or raw.get("id") or ""),
      "tool": tool,
      "sample_id": str(sample_id or raw.get("sample_id") or ""),
      "repository": raw.get("repository",""),
      "file_path": str(raw.get("file_path") or raw.get("path") or ""),
      "start_line": int(raw.get("start_line") or raw.get("line") or 0),
      "end_line": int(raw.get("end_line") or raw.get("start_line") or raw.get("line") or 0),
      "cwe": str(raw.get("cwe") or ""),
      "severity": str(raw.get("severity") or "unknown"),
      "title": str(raw.get("title") or raw.get("message") or raw.get("check_id") or "Finding"),
      "description": str(raw.get("description") or raw.get("message") or ""),
      "evidence": str(raw.get("evidence") or ""),
      "confidence": raw.get("confidence"),
      "runtime_seconds": raw.get("runtime_seconds"),
      "raw_reference": str(raw.get("raw_reference") or ""),
      "adjudication": raw.get("adjudication","pending")
    }
